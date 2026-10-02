from pathlib import Path
import sys,struct
sys.path.insert(0,'tools');import iso
for p,l,s,_ in iso.walk():
 if p.endswith('.IRX'):
  d=iso.read(l,s)
  if p=='LIQUID_F.IRX':Path('work/LIQUID_F.IRX').write_bytes(d)
  print(p,d.find(b'nFlC'))
  for o in range(0,len(d)-4,4):
   v=struct.unpack_from('<I',d,o)[0]
   if v>>26==15 and (v&65535)==0x436c:print('magic',hex(o))
