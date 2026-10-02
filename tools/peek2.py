from pathlib import Path
import struct
for name in ['GLOBALTEXT_JAPANESE','GAME']:
 d=Path('work/packs',name+'.bin').read_bytes()
 print(name)
 for o in range(0x200,0x380,16):print(hex(o),d[o:o+16].hex(' '))
 print(d[832:1600].decode('cp932','replace'))
