from pathlib import Path
import struct,json,lzokay
p=Path('work/AMALGA.PAK').read_bytes();records=json.loads(Path('work/pak_manifest.json').read_text()); errors=[];res=[]
for r in records:
 path=Path('work/packs',r['name']+'.bin')
 try:
  if not path.exists():
   out=bytearray()
   for pos in range(r['offset'],r['offset']+r['size'],32768):
    assert p[pos:pos+4]==b'nFlC',(r['name'],hex(pos))
    zs=struct.unpack_from('<H',p,pos+18)[0];us=struct.unpack_from('<I',p,pos+24)[0]
    out.extend(lzokay.decompress(p[pos+64:pos+64+zs],us))
   path.write_bytes(out)
  d=path.read_bytes();base=struct.unpack_from('<I',d,28)[0]
  for o in range(0x300,base,16):
   h,t,off,sz=struct.unpack_from('<4I',d,o)
   if t in [17,19,48] and base+off+sz<=len(d):res.append(dict(pack=r['name'],record=o,hash=h,type=t,offset=base+off,size=sz))
 except Exception as e:errors.append([r['name'],str(e)])
Path('work/resources.json').write_text(json.dumps(res,indent=2));print('Packs',len(records),'errors',errors,'text resources',len(res));print(res[:25])
