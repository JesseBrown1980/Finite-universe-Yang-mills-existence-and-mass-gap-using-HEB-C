# READ-ONLY independent verification of the d300 stream, from a fresh process.
import hashlib
S="D:/ASOLARIA-HOST8-ROOMS-300G/sector-%03d.rooms"; SEG=800000000; FIRST=341; COUNT=34; MIB=1048576
def rd(pos, n):
    out=bytearray()
    while n>0:
        k,o=divmod(pos,SEG)
        with open(S%(FIRST+k),"rb") as f:
            f.seek(o); b=f.read(min(n,SEG-o))
        out+=b; pos+=len(b); n-=len(b)
    return bytes(out)
hdr=rd(0,4096); line=hdr[:hdr.index(b"\n")].decode()
fld=dict(kv.split("=",1) for kv in line.split("|")[1:] if "=" in kv)
sb=int(fld["stream_bytes"]); pb=int(fld["payload_bytes"])
print("VERIFY_HDR|"+line.split("|",1)[1])
full=hashlib.sha256(hdr); shas=b""; pos=4096
while pos<sb:
    c=rd(pos,min(16*MIB,sb-pos)); full.update(c); shas+=hashlib.sha256(c).hexdigest().encode(); pos+=len(c)
mk=hashlib.sha256(shas).hexdigest()
print(f"VERIFY_STREAM|stream_bytes={sb}|payload_bytes={pb}|stream_sha256={full.hexdigest()}|payload_merkle_recomputed={mk}|merkle_match={int(mk==fld['payload_merkle'])}|json=0")
last=FIRST+sb//SEG; used=sb%SEG
with open(S%last,"rb") as f:
    f.seek(used); t=f.read()
print(f"VERIFY_TAIL|sector={last}|file_from={used}|bytes={len(t)}|tail_sha256={hashlib.sha256(t).hexdigest()}|json=0")
