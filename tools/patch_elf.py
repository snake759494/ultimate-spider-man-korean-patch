from pathlib import Path
import struct
p=bytearray(Path('work/SLPM_664.04').read_bytes())
assert struct.unpack_from('<I',p,0x27b4d0)[0]==0x24020001
assert struct.unpack_from('<I',p,0x27b4d4)[0]==0xa2220026
# Font bank: use the already loaded Japanese font for heading index 4.
# s0 is sp+4 here (stack is 16-byte aligned), hence its low byte is nonzero.
struct.pack_into('<I',p,0x27b4d0,0xae220010) # sw v0,16(s1)
struct.pack_into('<I',p,0x27b4d4,0xa2300026) # sb s0,38(s1) (initialized)
# Slot 4 is an alias, not a second owned font. Avoid loading the unused
# original heading font and avoid releasing the shared font twice.
assert struct.unpack_from('<I',p,0x27b350)[0]==0x0c0de93c
assert struct.unpack_from('<I',p,0x27b6f8)[0]==0x0c0de9c4
struct.pack_into('<I',p,0x27b350,0) # nop: load slot 4
struct.pack_into('<I',p,0x27b6f8,0) # nop: release slot 4
Path('build/SLPM_664.04').write_bytes(p)
