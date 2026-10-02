from pathlib import Path
import struct
p=Path('work/AMALGA.PAK').read_bytes()
for o in [0,0x38,0x3cc0,0x40e0,0x4118-8,0xa060,0xc030,0xc068,0xc800,0x1f80880]:
 print('\n',hex(o))
 for i in range(o,o+160,16):print(f'{i:08x}',p[i:i+16].hex(' '),''.join(chr(c) if 32<=c<127 else '.' for c in p[i:i+16]))
