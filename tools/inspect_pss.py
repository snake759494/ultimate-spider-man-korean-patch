from pathlib import Path
import struct
def packets(data):
 i=0
 while i<len(data):
  assert data[i:i+3]==b'\0\0\1',(hex(i),data[i:i+12])
  tag=data[i+3]
  if tag==0xb9:n=4
  elif tag==0xba:n=14+(data[i+13]&7) if data[i+4]&0xc0==0x40 else 12
  else:n=6+int.from_bytes(data[i+4:i+6],'big')
  yield i,tag,data[i:i+n];i+=n
def pts(p):return ((p[0]>>1&7)<<30)|(p[1]<<22)|((p[2]>>1)<<15)|(p[3]<<7)|(p[4]>>1)
if __name__=='__main__':
 for path in ['work/cinematics/41dab593.pss','build/cinematics/41dab593.pss']:
  print(path)
  for k,(i,t,p) in enumerate(packets(Path(path).read_bytes())):
   if k>=35:break
   print(hex(i),hex(t),len(p),p[6:19].hex(),pts(p[9:14])/90000 if t in (0xe0,0xbd) and p[7]&0x80 else '')
