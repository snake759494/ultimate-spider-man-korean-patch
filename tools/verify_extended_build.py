from pathlib import Path
import json,struct,lzokay,iso,re
dst=Path('build/Ultimate Spider-Man (Japan) [Korean-subtitle-test].iso')
original={r[0]:r for r in iso.walk()};patched={r[0]:r for r in iso.walk(str(dst))}
assert original.keys()==patched.keys()
for name in original:
 assert original[name][1]==patched[name][1]
 if name!='PACKS/AMALGA.PAK':assert original[name][2]==patched[name][2]
p=Path('build/AMALGA_extended.PAK').read_bytes();old=Path('work/AMALGA.PAK').read_bytes();records=json.loads(Path('work/pak_manifest.json').read_text())
changes=[]
for r in records:
 at=r['record'];h,t,off,raw=struct.unpack_from('<4I',p,at);reserved=struct.unpack_from('<I',p,at+24)[0];off+=0xc800
 assert off+reserved<=len(p)
 data=p[off:off+reserved]
 if data==old[r['offset']:r['offset']+r['size']]:continue
 assert r['name'] in ('GAME','GLOBALTEXT_JAPANESE')
 count=struct.unpack_from('<I',data,8)[0]&0x7fffffff;decoded=bytearray()
 for i in range(count):
  b=data[i*32768:(i+1)*32768];assert b[:4]==b'nFlC';z=struct.unpack_from('<H',b,18)[0];n=struct.unpack_from('<I',b,24)[0]
  assert struct.unpack_from('<I',b,44)[0]==len(decoded)
  decoded.extend(lzokay.decompress(b[64:64+z],n))
 target=Path('build/GAME_extended.bin' if r['name']=='GAME' else 'build/GLOBALTEXT_JAPANESE.bin')
 assert decoded==target.read_bytes(),r['name'];changes.append(r['name'])
 assert len(decoded)+struct.unpack_from('<I',p,at+40)[0]==raw
assert old[struct.unpack_from('<I',old,0x2c)[0]:]==p[struct.unpack_from('<I',p,0x2c)[0]:]
game=Path('build/GAME_extended.bin').read_bytes();base=struct.unpack_from('<I',game,0x1c)[0];aux=struct.unpack_from('<I',game,0x28)[0]
for at in range(0x300,0x930,16):
 h,t,off,size=struct.unpack_from('<4I',game,at)
 assert off+base+size<=len(game),(hex(at),off,size)
poolcount=struct.unpack_from('<I',game,0xb4)[0]&0xffffff
for at in range(0xe70,0xe70+poolcount*12,12):
 flags,count,off=struct.unpack_from('<III',game,at);size=flags&0xffff;count&=0xffff
 assert len(game)<=off<=len(game)+aux
 assert off+size*count<=len(game)+aux
maps,ms=struct.unpack_from('<II',p,0x24);budget=struct.unpack_from('<I',p,0x34)[0]
for at in range(maps,maps+ms,144):
 parts=[struct.unpack_from('<4I',p,at+16+i*16) for i in range(8)]
 assert parts[0][2]>=len(game)+aux
 assert sum(size*count for _,_,size,count in parts)<=budget
mapping=json.loads(Path('translation/glyph_map_extended.json').read_text(encoding='utf-8'))
assert len(mapping)==2350 and len(set(mapping.values()))==2350
off,size=struct.unpack_from('<II',game,0x678);font=game[base+off:base+off+size].decode('ascii')
assert 'numgood 2430' in font
chars=set(int(c) for c in re.findall(r'(\d+) x ',font));assert set(mapping.values())<=chars
assert all(0xa0 not in c.to_bytes(2,'big') for c in mapping.values())
with dst.open('rb') as f:
 for name,artifact in [('PACKS/AMALGA.PAK','build/AMALGA_extended.PAK'),('SLPM_664.04','build/runtime/SLPM_664.04')]:
  _,l,n,_=patched[name];f.seek(l*2048);assert f.read(n)==Path(artifact).read_bytes()
 ml=patched['PACKS/MOVIES.PAK'][1]
 for i,r in enumerate(json.loads(Path('work/movie_manifest.json').read_text())):
  ext='ipu' if r['type']==32 else 'pss'
  file=Path('build/cinematics')/('%08x.%s'%(r['hash'],ext))
  if not file.exists():continue
  f.seek(ml*2048+0x308+i*16);h,t,off,n=struct.unpack('<4I',f.read(16));assert h==r['hash'] and n==file.stat().st_size
  f.seek(ml*2048+r['offset']);assert f.read(n)==file.read_bytes()
print('PASS: ISO geometry, 615 pack bounds, NFLC round trips, allocation pools, 5 memory maps, 2350 glyphs, cinematic resources, runtime ELF')
