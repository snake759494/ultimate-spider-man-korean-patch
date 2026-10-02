from pathlib import Path
import zlib,struct,json
p=Path('work/AMALGA.PAK').read_bytes()
for r in json.loads(Path('work/pak_manifest.json').read_text()):
 if r['name'] not in ['GAME','GLOBALTEXT_JAPANESE']:continue
 o=r['offset'];zs=struct.unpack_from('<H',p,o+18)[0];us=struct.unpack_from('<I',p,o+24)[0];d=Path('work/packs',r['name']+'.bin').read_bytes()[:us];c=p[o+64:o+64+zs]
 print(r['name'],p[o:o+64].hex(' '),'compressed crc/adler',hex(zlib.crc32(c)),hex(zlib.adler32(c)),'uncomp',hex(zlib.crc32(d)),hex(zlib.adler32(d)))
