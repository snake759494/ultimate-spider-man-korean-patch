from pathlib import Path
import struct,capstone
p=Path('work/SLPM_664.04').read_bytes();md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS64|capstone.CS_MODE_LITTLE_ENDIAN)
for o in range(0x1000,len(p)-4,4):
 v=struct.unpack_from('<I',p,o)[0]
 if v>>26==15 and (v&65535) in [0x436c,0x6e46]:
  print('Magic candidate',hex(o))
  for x in md.disasm(p[o-32:o+96],o-32+0xff000): print(hex(x.address),x.mnemonic,x.op_str)
