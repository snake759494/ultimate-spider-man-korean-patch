from pathlib import Path
import subprocess,struct,json,sys
sys.path.insert(0,'work/compiler')
from elftools.elf.elffile import ELFFile
out=Path('build/runtime');out.mkdir(exist_ok=True)
mapping=json.loads(Path('translation/glyph_map.json').read_text(encoding='utf-8'))
text='스파이더맨'
encoded=b''.join(mapping[c].to_bytes(2,'big') for c in text)
Path('tools/subtitle_test_text.h').write_text('static const char test_text[]={'+','.join(str(v) for v in encoded)+',0};\n')
# Bridges isolate the game's legacy 64-bit register ABI from the C o32 ABI.
def save_regs(regs,base=16):return '\n'.join(f'sd ${r},{base+i*8}($sp)' for i,r in enumerate(regs))
def load_regs(regs,base=16):return '\n'.join(f'ld ${r},{base+i*8}($sp)' for i,r in enumerate(regs))
saved=[16,17,18,19,20,21,22,23,28,30,31]
allregs=list(range(1,26))+[28,30,31]
asm=f'''.set noreorder
.set noat
.set mips3
.text
.globl render_hook
render_hook:
addiu $sp,$sp,-112
{save_regs(saved)}
jal subtitle_frame
nop
jal 0x58cbec
nop
{load_regs(saved)}
jr $ra
addiu $sp,$sp,112
.globl sound_hook
sound_hook:
addiu $sp,$sp,-256
{save_regs(allregs)}
move $a0,$v1
jal subtitle_sound
nop
{load_regs(allregs)}
addiu $sp,$sp,256
lbu $v0,0x9a($v1)
ori $v0,$v0,1
j 0x5cd458
nop
.globl draw_line
.globl stop_hook
stop_hook:
addiu $sp,$sp,-256
{save_regs(allregs)}
jal subtitle_stop
nop
{load_regs(allregs)}
addiu $sp,$sp,256
addiu $sp,$sp,-32
sd $s0,0($sp)
j 0x5cd388
nop
draw_line:
lw $8,16($sp)
addiu $sp,$sp,-32
sd $ra,16($sp)
mtc1 $a3,$f12
.word 0x44886800
mtc1 $zero,$f14
lui $8,0x3f80
.word 0x44887800
mtc1 $8,$f16
jal 0x593f50
nop
ld $ra,16($sp)
jr $ra
addiu $sp,$sp,32
.globl memcpy_hook
memcpy_hook:
bnez $a0,1f
nop
lui $t0,0xb
sw $ra,-0x1000($t0)
sw $a1,-0xffc($t0)
sw $a2,-0xff8($t0)
1:
move $t0,$a0
sltiu $v0,$a2,0x20
j 0x5ff804
nop
'''
(out/'bridge.S').write_text(asm)
cc='work/compiler/ziglang/zig.exe'
flags=['cc','-target','mipsel-linux-musl','-mcpu=mips2-fp64','-mabi=32','-msoft-float','-fno-pic','-mno-abicalls','-nostdlib','-G0','-fno-stack-protector','-O1']
for src,obj in [('tools/subtitle_runtime.c',out/'runtime.o'),(out/'bridge.S',out/'bridge.o')]:
 p=subprocess.run([cc,*flags,'-c',str(src),'-o',str(obj)],capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
elf=out/'runtime.elf'
p=subprocess.run([cc,*flags,str(out/'runtime.o'),str(out/'bridge.o'),'-Wl,-T,tools/subtitle_runtime.ld','-Wl,--build-id=none','-static','-o',str(elf)],capture_output=True)
if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
with elf.open('rb') as f:
 e=ELFFile(f);symbols={s.name:s.entry.st_value for s in e.get_section_by_name('.symtab').iter_symbols()}
 sections=[s for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
 start=min(s['sh_addr'] for s in sections);end=max(s['sh_addr']+s['sh_size'] for s in sections)
 payload=bytearray(end-start)
 for s in sections:
  if s['sh_type']!='SHT_NOBITS':payload[s['sh_addr']-start:s['sh_addr']-start+s['sh_size']]=s.data()
assert start==0xa0000 and end<0x100000
p=bytearray(Path('build/SLPM_664.04').read_bytes());offset=0x64a000
assert offset+len(payload)<=len(p)
p[offset:offset+len(payload)]=payload
assert struct.unpack_from('<H',p,44)[0]==1
ph=struct.unpack_from('<I',p,28)[0]+32
struct.pack_into('<8I',p,ph,1,offset,start,start,len(payload),len(payload),7,4096)
struct.pack_into('<H',p,44,2)
# Debug section headers beyond the loaded segment are overwritten by payload.
struct.pack_into('<I',p,32,0);struct.pack_into('<HH',p,48,0,0)
# The old world-view hook draws underneath later comic panels. This call ends
# the final full-screen overlay scene, after every panel has been submitted.
assert struct.unpack_from('<I',p,0x196c0c)[0]==0x0c1632fb
struct.pack_into('<I',p,0x196c0c,0x0c000000|(symbols['render_hook']>>2))
assert struct.unpack_from('<I',p,0x4ce450)[0]==0x9062009a
struct.pack_into('<2I',p,0x4ce450,0x08000000|(symbols['sound_hook']>>2),0)
assert struct.unpack_from('<2I',p,0x4ce380)==(0x27bdffe0,0xffb00000)
struct.pack_into('<2I',p,0x4ce380,0x08000000|(symbols['stop_hook']>>2),0)
# Diagnostic memcpy_hook is retained in symbols but is not installed in builds.
(out/'SLPM_664.04').write_bytes(p)
(out/'symbols.json').write_text(json.dumps(symbols,indent=2))
print('payload',hex(start),len(payload),'hooks',hex(symbols['render_hook']),hex(symbols['sound_hook']))
