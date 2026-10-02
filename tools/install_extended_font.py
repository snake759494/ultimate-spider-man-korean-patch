from pathlib import Path
import json,struct,lzokay,iso,sys
d=Path(sys.argv[1] if len(sys.argv)>1 else 'build/GAME_extended.bin').read_bytes();chunks=[];off=0
while off<len(d):
 lo=1;hi=min(131072,len(d)-off)//128;best=None
 while lo<=hi:
  mid=(lo+hi)//2;raw=d[off:off+mid*128];comp=lzokay.compress(raw)
  if len(comp)<=32704:best=(raw,comp);lo=mid+1
  else:hi=mid-1
 assert best;chunks.append(best);off+=len(best[0])
total=sum(len(c) for u,c in chunks);uz=cz=0;out=bytearray()
for i,(u,c) in enumerate(chunks):
 h=bytearray(64);h[:4]=b'nFlC';struct.pack_into('<HHII',h,4,0x101,i,0x80000000|len(chunks),(0x80000000 if i<len(chunks)-1 else 0)|(0x8000 if i else 0))
 struct.pack_into('<HH7I',h,16,0x901,len(c),0,len(u),0,total,cz,len(d),uz)
 out.extend(h+c+bytes(32768-64-len(c)));uz+=len(u);cz+=len(c)
assert b''.join(lzokay.decompress(bytes(out[i*32768+64:i*32768+64+len(c)]),len(u)) for i,(u,c) in enumerate(chunks))==d
p=bytearray(Path('build/AMALGA.PAK').read_bytes());tail=struct.unpack_from('<I',p,0x2c)[0];p[tail:tail]=out
r=next(r for r in json.loads(Path('work/pak_manifest.json').read_text()) if r['name']=='GAME');rec=r['record']
aux=struct.unpack_from('<I',d,0x28)[0]
struct.pack_into('<II',p,rec+8,tail-0xc800,len(d)+aux);struct.pack_into('<I',p,rec+40,aux);struct.pack_into('<I',p,rec+24,len(out));struct.pack_into('<I',p,0x2c,tail+len(out))
# Each memory map reserves a fixed permanent GAME slot. The directory size
# alone does not resize it; subsequent packages would overwrite the new font.
maps,maps_size=struct.unpack_from('<II',p,0x24)
old_slot=struct.unpack_from('<I',p,maps+24)[0]
new_slot=max(old_slot,(len(d)+aux+10240+4095)//4096*4096)
for at in range(maps,maps+maps_size,144):
 assert struct.unpack_from('<4I',p,at+16)==(0,1,old_slot,1)
 struct.pack_into('<I',p,at+24,new_slot)
struct.pack_into('<I',p,0x34,struct.unpack_from('<I',p,0x34)[0]+new_slot-old_slot)
Path('build/AMALGA_extended.PAK').write_bytes(p)
dst=Path('build/Ultimate Spider-Man (Japan) [Korean-subtitle-test].iso')
_,lba,size,record=next(r for r in iso.walk() if r[0]=='PACKS/AMALGA.PAK')
with dst.open('r+b') as f:
 f.seek(lba*2048);f.write(p);f.write(bytes((-len(p))%2048));end=f.tell()
 # The expanded archive fits in zero padding before a nonzero final disc sector.
 # Preserve that sector, original disc size, and original PVD volume geometry.
 with open(iso.ISO,'rb') as original:
  original.seek(lba*2048+size)
  assert not any(original.read(end-(lba*2048+size))),'archive expansion overlaps source data'
  original.seek(end)
  while chunk:=original.read(1048576):f.write(chunk)
  f.truncate(original.tell())
  original.seek(16*2048+80);geometry=original.read(8)
 f.seek(record+10);f.write(struct.pack('<I',len(p))+struct.pack('>I',len(p)))
 f.seek(16*2048+80);f.write(geometry)
print('GAME',len(d),'blocks',len(chunks),'PAK',len(p),'ISO',dst.stat().st_size)
