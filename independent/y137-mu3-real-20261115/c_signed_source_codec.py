#!/usr/bin/env python3
"""#137 Stage C candidate signed source spool; exact, canonical, length-bound.

A production 3x4 S3 signed K3/Q4 spool uses 11-byte header <QBBB>
(canonical address, global conjugation orbit weight, shell code 3/4,
two frozen-energy samples), then 16 signed-magnitude variable length lanes
in sample-major order. Each lane: 1 byte (bit7 sign, low7 byte count 0..24),
followed by that many little-endian unsigned magnitude bytes. No negative
zero; no nonminimal magnitude. Strict <2^192 per signed magnitude.
This is *format/fixture*, not a completed real-source certificate.
"""
import hashlib
import io
import os
import struct
import sys
import tempfile

HEADER = struct.Struct("<QBBB")
LANES = 8
SAMPLES = 2
MAX_BITS = 192
MAX_ADDR = 6**13
ALLOWED_SHELLS = (3,4)

class Refuse(Exception):
    pass

def need(ok,why):
    if not ok:
        raise Refuse(why)

def enc_lane(value):
    need(isinstance(value,int),"C_codec_lane_not_int")
    mag=abs(value)
    need(mag.bit_length() <= MAX_BITS,"C_codec_signed_lane_too_wide")
    size=(mag.bit_length()+7)//8
    need(size <= MAX_BITS//8,"C_codec_lane_bytes_exceeded")
    sign=0x80 if value<0 else 0
    return bytes((size|sign,))+mag.to_bytes(size,"little")

def dec_lane(stream):
    h=stream.read(1)
    need(len(h)==1,"C_codec_short_lane_prefix")
    n=h[0]&0x7f
    sign=h[0]&0x80
    need(n<=MAX_BITS//8,"C_codec_lane_length_out_of_range")
    data=stream.read(n)
    need(len(data)==n,"C_codec_short_lane_magnitude")
    need(n==0 or data[-1]!=0,"C_codec_nonminimal_magnitude")
    need(not sign or n>0,"C_codec_negative_zero")
    mag=int.from_bytes(data,"little")
    need(mag.bit_length()<=MAX_BITS,"C_codec_lane_value_out_of_range")
    return -mag if sign else mag

def encode(address,weight,shell,values):
    need(0<=address<MAX_ADDR,"C_codec_canonical_address_range")
    need(weight in (1,2,3,6),"C_codec_bad_orbit_weight")
    need(shell in ALLOWED_SHELLS,"C_codec_bad_shell")
    need(len(values)==SAMPLES and all(len(v)==LANES for v in values),
         "C_codec_expected_two_eight_lane_vectors")
    data=bytearray(HEADER.pack(address,weight,shell,SAMPLES))
    for sample in values:
        for value in sample:
            data.extend(enc_lane(value))
    return bytes(data)

def decode(stream):
    header=stream.read(HEADER.size)
    if not header:
        return None
    need(len(header)==HEADER.size,"C_codec_short_record_header")
    address,weight,shell,ns=HEADER.unpack(header)
    need(address<MAX_ADDR,"C_codec_address_out_of_range")
    need(weight in (1,2,3,6),"C_codec_invalid_orbit_weight")
    need(shell in ALLOWED_SHELLS,"C_codec_invalid_shell")
    need(ns==SAMPLES,"C_codec_invalid_sample_count")
    values=tuple(tuple(dec_lane(stream) for _ in range(LANES))
                 for _ in range(SAMPLES))
    return address,weight,shell,values

def verified_read(path,expected_sha,expected_rows,shell):
    digest=hashlib.sha256()
    records=0
    last_address=None
    with open(path,"rb") as stream:
        while True:
            start=stream.tell()
            row=decode(stream)
            if row is None:
                break
            finish=stream.tell()
            stream.seek(start)
            chunk=stream.read(finish-start)
            digest.update(chunk)
            address,w,current_shell,values=row
            need(current_shell==shell,"C_codec_shell_partition")
            if last_address is not None:
                need(address>last_address,"C_codec_duplicate_or_out_of_order_address")
            last_address=address
            need(encode(address,w,current_shell,values)==chunk,
                 "C_codec_roundtrip_noncanonical_bytes")
            records+=1
    need(records==expected_rows,"C_codec_total_record_count_changed")
    need(digest.hexdigest()==expected_sha,"C_codec_source_digest_changed")
    return records,digest.hexdigest()

def toy():
    vectors=((0,1,-1,13,-13,(1<<191)-1,-((1<<191)-1),19),
             (7,-7,0,1,-2,3,-4,1<<190))
    sample=encode(18,6,4,vectors)
    need(decode(io.BytesIO(sample))==(18,6,4,vectors),
         "C_codec_exact_signed_roundtrip")
    need(decode(io.BytesIO(b"")) is None,"C_codec_eof")
    with tempfile.TemporaryDirectory() as temp:
        path=os.path.join(temp,"signed.v1")
        with open(path,"wb") as f:f.write(sample)
        digest=hashlib.sha256(sample).hexdigest()
        verified_read(path,digest,1,4)
        count=0
        def fail(label,data):
            nonlocal count
            try:
                decode(io.BytesIO(data))
            except Refuse:
                count+=1
            else:
                raise Refuse("C_codec_"+label+"_corruption_accepted")
        fail("short_header",sample[:4])
        fail("short_lane",sample[:-2])
        fail("negative_zero",sample[:HEADER.size]+bytes((0x80,))+sample[HEADER.size+1:])
        fail("invalid_lane_length",sample[:HEADER.size]+bytes((25,))+sample[HEADER.size+1:])
        fail("wrong_shell",sample[:9]+bytes((5,))+sample[10:])
        fail("wrong_weight",sample[:8]+bytes((4,))+sample[9:])
        fail("wrong_sample_count",sample[:10]+bytes((1,))+sample[11:])
        try:
            encode(18,6,4,((1<<192,)*8, vectors[1]))
        except Refuse:
            count+=1
        else:
            raise Refuse("C_codec_oversized_signed_source_accepted")
        altered=encode(18,6,4,(tuple(-v for v in vectors[0]),vectors[1]))
        need(altered!=sample and hashlib.sha256(altered).hexdigest()!=digest,
             "C_codec_signed_flip_not_detectable")
        with open(path,"wb") as f:f.write(altered)
        try:
            verified_read(path,digest,1,4)
        except Refuse:
            count+=1
        else:
            raise Refuse("C_codec_signed_source_fingerprint_attack_accepted")
    need(count==9,"C_codec_incomplete_negative_controls")
    print("Y137_C_CODEC_TOY|samples=2|lanes_per_sample=8"+
          "|signed_192bit=PASS|exact_roundtrip=PASS|source_SHA=PASS"+
          "|bad_header_short_lane_negative_zero_length_shell_weight_samples=REFUSED"+
          "|oversized_lane=REFUSED|signed_flip_wrong_SHA=REFUSED"+
          "|negative_controls=9|real_K3_Q4_spool=NOT_COMPUTED"+
          "|whole_mu3=NOT_COMPUTED|Wilson_weight=HOLD|json=0")

def main(argv):
    try:
        need(argv==["toy"],"C_codec_usage")
        toy()
    except (Refuse,ValueError,OSError) as exc:
        print("Y137_C_CODEC_REFUSE|reason="+str(exc)+"|json=0",flush=True)
        raise SystemExit(1) from None

if __name__=="__main__":
    main(sys.argv[1:])
