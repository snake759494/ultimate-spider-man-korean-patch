from pathlib import Path
import struct,json,lzokay
p=Path('work/AMALGA.PAK').read_bytes()
for r in json.loads(Path('work/pak_manifest.json').read_text()):
 if r['name'] not in ['GAME','GLOBALTEXT_JAPANESE']:continue
 d=Path('build',r['name']+'.bin').read_bytes();print(r['name']);up=0
 for i,o in enumerate(range(r['offset'],r['offset']+r['size'],32768)):
  zs=struct.unpack_from('<H',p,o+18)[0];us=struct.unpack_from('<I',p,o+24)[0];cp=lzokay.compress(d[up:up+us]);print(i,struct.unpack_from('<16I',p,o),len(cp));up+=us
