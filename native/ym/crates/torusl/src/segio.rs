//! One byte stream over either a single file/device or a run of equal-length
//! sector files (the Host8 room store layout: `sector-NNN.rooms`, 8-byte rooms).
//!
//! Spec forms:
//!   `<path>`                                   a single file or `//./PhysicalDriveN`
//!   `seg:<first>:<count>:<seglen>:<prefix>`    files `<prefix>NNN.rooms`, NNN = first..first+count
//!                                              (zero padded to 3), each exactly `seglen` bytes
//!
//! A segmented stream never grows or truncates a sector file: every file must
//! already be `seglen` bytes long, and a read or write past `count * seglen` fails.

use std::fs::{File, OpenOptions};
use std::io::{Error, ErrorKind, Read, Result, Seek, SeekFrom, Write};

pub struct Dev {
    files: Vec<File>,
    names: Vec<String>,
    seglen: u64, // 0 = single unsegmented file
    pos: u64,
}

pub fn open(spec: &str, write: bool) -> Result<Dev> {
    let oo = |p: &str| OpenOptions::new().read(true).write(write).open(p);
    if let Some(rest) = spec.strip_prefix("seg:") {
        let mut it = rest.splitn(4, ':');
        let bad = || Error::new(ErrorKind::InvalidInput, "seg spec: seg:<first>:<count>:<seglen>:<prefix>");
        let first: u64 = it.next().and_then(|s| s.parse().ok()).ok_or_else(bad)?;
        let count: u64 = it.next().and_then(|s| s.parse().ok()).ok_or_else(bad)?;
        let seglen: u64 = it.next().and_then(|s| s.parse().ok()).ok_or_else(bad)?;
        let prefix = it.next().ok_or_else(bad)?;
        if count == 0 || seglen == 0 {
            return Err(bad());
        }
        let mut files = Vec::new();
        let mut names = Vec::new();
        for k in first..first + count {
            let name = format!("{prefix}{k:03}.rooms");
            let f = oo(&name)?;
            if f.metadata()?.len() != seglen {
                return Err(Error::new(ErrorKind::InvalidData, format!("{name}: length != seglen")));
            }
            files.push(f);
            names.push(name);
        }
        Ok(Dev { files, names, seglen, pos: 0 })
    } else {
        Ok(Dev { files: vec![oo(spec)?], names: vec![spec.to_string()], seglen: 0, pos: 0 })
    }
}

impl Dev {
    /// Total addressable bytes of a segmented stream (None for a single file).
    pub fn capacity(&self) -> Option<u64> {
        (self.seglen > 0).then(|| self.seglen * self.files.len() as u64)
    }

    pub fn names(&self) -> &[String] {
        &self.names
    }

    /// Flush every underlying file to stable storage.
    pub fn sync(&self) -> Result<()> {
        for f in &self.files {
            f.sync_all()?;
        }
        Ok(())
    }

    /// (file index, offset inside it, bytes available in it) for the current position.
    fn at(&self) -> Result<(usize, u64, u64)> {
        if self.seglen == 0 {
            return Ok((0, self.pos, u64::MAX));
        }
        let k = self.pos / self.seglen;
        if k >= self.files.len() as u64 {
            return Err(Error::new(ErrorKind::UnexpectedEof, "past end of segmented stream"));
        }
        let o = self.pos % self.seglen;
        Ok((k as usize, o, self.seglen - o))
    }
}

impl Read for Dev {
    fn read(&mut self, buf: &mut [u8]) -> Result<usize> {
        if buf.is_empty() {
            return Ok(0);
        }
        let (k, o, room) = match self.at() {
            Ok(v) => v,
            Err(_) if self.seglen > 0 => return Ok(0),
            Err(e) => return Err(e),
        };
        let take = buf.len().min(usize::try_from(room).unwrap_or(usize::MAX));
        let f = &mut self.files[k];
        f.seek(SeekFrom::Start(o))?;
        let got = f.read(&mut buf[..take])?;
        self.pos += got as u64;
        Ok(got)
    }
}

impl Write for Dev {
    fn write(&mut self, buf: &[u8]) -> Result<usize> {
        if buf.is_empty() {
            return Ok(0);
        }
        let (k, o, room) = self.at()?;
        let take = buf.len().min(usize::try_from(room).unwrap_or(usize::MAX));
        let f = &mut self.files[k];
        f.seek(SeekFrom::Start(o))?;
        let put = f.write(&buf[..take])?;
        self.pos += put as u64;
        Ok(put)
    }

    fn flush(&mut self) -> Result<()> {
        for f in &mut self.files {
            f.flush()?;
        }
        Ok(())
    }
}

impl Seek for Dev {
    fn seek(&mut self, to: SeekFrom) -> Result<u64> {
        self.pos = match to {
            SeekFrom::Start(p) => p,
            SeekFrom::Current(d) => self.pos.checked_add_signed(d).ok_or_else(|| Error::new(ErrorKind::InvalidInput, "seek"))?,
            SeekFrom::End(_) => return Err(Error::new(ErrorKind::Unsupported, "seek from end")),
        };
        Ok(self.pos)
    }
}
