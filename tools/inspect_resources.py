from pathlib import Path
import struct,re,json
p=Path('work/packs/GLOBALTEXT_JAPANESE.bin').read_bytes()
for o in [0x340,0x340+0x7ada,0x340+0x7adc,0x340+0xd574]:
 print(hex(o),p[o:o+100].hex(' '))
d=Path('work/packs/GAME.bin').read_bytes()
print(d[0x3de0:0x3f00].decode('ascii','replace'))
for i in range(0x300,0xee0,16):
 if any(d[i:i+16]): print(f'{i:04x}',d[i:i+16].hex(' '))
