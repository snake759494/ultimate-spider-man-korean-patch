from pathlib import Path
import struct,sys
p=Path('work/SLPM_664.04').read_bytes();words=struct.unpack('<'+'I'*(len(p)//4),p[:len(p)//4*4])
arg=sys.argv[1]
if arg.startswith('0x'):targets=[int(arg,16)]
else:
 b=arg.encode();targets=[];o=p.find(b)
 while o>=0:targets.append(o+0xff000);o=p.find(b,o+1)
for target in targets:
 print('TARGET',hex(target),'file',hex(target-0xff000))
 hi=(target+0x8000)>>16;lo=target&65535
 for i,w in enumerate(words[:0x640000//4]):
  if w>>26==15 and (w&65535) in (hi,target>>16):
   reg=w>>16&31
   for j in range(i+1,min(i+25,len(words))):
    v=words[j]
    if v>>26 in (9,13,35,32,36,37,33) and v>>21&31==reg and v&65535==lo:
     print('REF',hex(i*4),hex(j*4))
  if w>>26 in (2,3) and (w&0x3ffffff)*4==target:print('CALL',hex(i*4))
