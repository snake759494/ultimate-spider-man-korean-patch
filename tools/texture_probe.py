from pathlib import Path
import struct
p=Path('work/packs/GAME.bin').read_bytes();o=0xee0+0xee9a0
print(hex(o),p[o:o+384].hex(' '))
for n in ['GLOBALTEXT_JAPANESE','GAME','S01_IGC1_PACK','S05_IGC1_PACK']:
 f=Path('work/packs',n+'.bin')
 if f.exists():
  d=f.read_bytes();print(n,[(hex(i),d[i:i+32]) for i in range(len(d)) if d[i:i+4] in [b'TIM2',b'~cro']][:10])
