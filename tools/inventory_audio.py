from pathlib import Path
import struct,json,iso
d=Path('work/sounds_header.bin').read_bytes();base=struct.unpack_from('<I',d,28)[0]
sl=next(l for p,l,s,r in iso.walk() if p=='PACKS/SOUNDS.PAK')
rows=[]
with open(iso.ISO,'rb') as f:
 for o in range(0x308,base-15,16):
  h,t,off,n=struct.unpack_from('<4I',d,o)
  if t!=31:break
  if not n:continue
  f.seek(sl*2048+base+off);head=f.read(0x1000)
  assert head[:8]==b'WAVEBK11',(o,head[:16])
  name=head[0x20:0x40].split(b'\0')[0].decode('ascii');count,table=struct.unpack_from('<2I',head,0x40)
  f.seek(sl*2048+base+off);bank=f.read(max(table+count*40,0x1000));streams=[]
  for i in range(count):
   pos=table+i*40;sh,codec,flags,mask,pad,size,samples,group,params,coefs,so,rate=struct.unpack_from('<IBBBB6IH',bank,pos)
   streams.append(dict(hash=sh,codec=codec,flags=flags,channels=2 if mask==3 else 1,size=size,samples=samples,offset=so,rate=rate,duration=round(samples/rate,3) if rate else 0))
  rows.append(dict(name=name,hash=h,offset=base+off,size=n,count=count,streams=streams))
Path('work/audio_inventory.json').write_text(json.dumps(rows,indent=2))
print([(r['name'],r['count']) for r in rows]);print('banks',len(rows),'streams',sum(r['count'] for r in rows))
