from pathlib import Path
import struct,capstone
p=Path('work/LIQUID_F.IRX').read_bytes();sh=struct.unpack_from('<I',p,32)[0];n=struct.unpack_from('<H',p,48)[0]
for i in range(n):print(i,struct.unpack_from('<10I',p,sh+40*i))
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32|capstone.CS_MODE_LITTLE_ENDIAN)
lines=[]
for o in range(0x80,0x5900,4):
 ins=list(md.disasm(p[o:o+4],o-0x80))
 if ins:lines.append(f'{o:06x} {ins[0].address:06x} {ins[0].mnemonic} {ins[0].op_str}')
Path('work/iop_disasm.txt').write_text('\n'.join(lines))
print(p[23200:23600])
