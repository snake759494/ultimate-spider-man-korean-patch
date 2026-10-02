"""Repack MPEG video and unchanged ADPCM into PS2-style 16 KiB packs."""
from pathlib import Path
from inspect_pss import packets,pts
import json
src=Path('work/cinematics/41dab593.pss');original=list(packets(src.read_bytes()))
new=list(packets(Path('build/cinematics/attract_video.ps').read_bytes()))
audio=[p for _,t,p in original if t==0xbd]
system=next(p for _,t,p in original if t==0xbb)
pack=next(p for _,t,p in original if t==0xba)
def putpts(n,prefix):
 return bytes([(prefix<<4)|(((n>>30)&7)<<1)|1,(n>>22)&255,((n>>15)&127)*2+1,(n>>7)&255,(n&127)*2+1])
result=bytearray();ai=0;clock=0
def begin():
 result.extend(pack)
 if len(result)==14:result.extend(system)
def remain():return 16384-len(result)%16384
def pad():
 n=remain()
 if n<16384:
  assert n>=6,n
  result.extend(b'\0\0\1\xbe'+(n-6).to_bytes(2,'big')+b'\xff'*(n-6))
def emit(p):
 if not len(result)%16384:begin()
 n=remain()
 if len(p)>n or 0<n-len(p)<6:
  pad();begin()
 result.extend(p)
for _,tag,p in new:
 if tag!=0xe0:continue
 flags=p[7];h=bytearray(p[9:9+p[8]])
 if flags&0x80:
  n=pts(h[:5])-3003;h[:5]=putpts(n,h[0]>>4);clock=n/90000
  if flags&0x40:
   n=pts(h[5:10])-3003;h[5:10]=putpts(n,h[5]>>4);clock=n/90000
  while ai<len(audio) and pts(audio[ai][9:14])/90000<=clock:
   emit(audio[ai]);ai+=1
 h.extend(b'\xff'*max(0,10-len(h)))
 body=bytes([0x83,flags,len(h)])+h+p[9+p[8]:]
 emit(b'\0\0\1\xe0'+len(body).to_bytes(2,'big')+body)
for p in audio[ai:]:emit(p)
result.extend(b'\0\0\1\xb9')
assert len(result)<=src.stat().st_size
assert b''.join(p for _,t,p in packets(result) if t==0xbd)==b''.join(audio)
assert all(i%16384==0 for i,t,p in packets(result) if t==0xba)
Path('build/cinematics/41dab593.pss').write_bytes(result)
q=Path('build/cinematics/attract.quality.json')
metadata=json.loads(q.read_text()) if q.exists() else {}
metadata.update(bytes=len(result),pack_size=16384,audio_packets=len(audio),audio_preserved=True,first_video_pts=0.19205555555555556)
q.write_text(json.dumps(metadata,indent=2))
print('PS2 packs',len(result),'bytes; original audio packets preserved:',len(audio))
