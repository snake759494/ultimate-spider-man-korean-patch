from pathlib import Path
import struct,json,lzokay,re
p=Path('work/AMALGA.PAK').read_bytes(); records=[]
Path('work/packs').mkdir(exist_ok=True)
for o in range(0x38,0xc068,80):
 v=struct.unpack_from('<12I',p,o);name=p[o+48:o+80].split(b'\0')[0].decode();start=v[2]+0xc800;size=v[6]
 records.append(dict(name=name,record=o,offset=start,size=size,uncompressed=v[3]))
 if name not in ['GAME','GLOBALTEXT_JAPANESE','GLOBALTEXT_ENGLISH']:continue
 out=bytearray()
 for pos in range(start,start+size,32768):
  assert p[pos:pos+4]==b'nFlC'
  zs=struct.unpack_from('<H',p,pos+18)[0];us=struct.unpack_from('<I',p,pos+24)[0]
  out.extend(lzokay.decompress(p[pos+64:pos+64+zs],us))
 Path('work/packs',name+'.bin').write_bytes(out)
 print(name,len(out),out[:128].hex(' '))
 ss=[(m.start(),m.group().decode()) for m in re.finditer(rb'[ -~]{5,}',out)]
 Path('work/packs',name+'_strings.txt').write_text('\n'.join(f'{a:08x} {s}' for a,s in ss))
 print(ss[:25])
Path('work/pak_manifest.json').write_text(json.dumps(records,indent=2))
