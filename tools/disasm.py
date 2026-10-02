from pathlib import Path
import capstone,sys
p=Path('work/SLPM_664.04').read_bytes();md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS64|capstone.CS_MODE_LITTLE_ENDIAN)
a=int(sys.argv[1],16);n=int(sys.argv[2],0) if len(sys.argv)>2 else 256
for o in range(a,a+n,4):
 inst=list(md.disasm(p[o:o+4],o+0xff000));print(f'{o:08x}',(' '.join([inst[0].mnemonic,inst[0].op_str])) if inst else p[o:o+4].hex())
