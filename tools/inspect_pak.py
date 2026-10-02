from pathlib import Path
import re,struct
p=Path('work/AMALGA.PAK').read_bytes()
ss=[(m.start(),m.group().decode('ascii')) for m in re.finditer(rb'[ -~]{6,}',p)]
Path('work/pak_strings.txt').write_text('\n'.join(f'{a:08x} {s}' for a,s in ss))
print('\n'.join(f'{a:08x} {s}' for a,s in ss if any(t in s.lower() for t in ['font','globaltext','japanese','credits']))[:16000])
print('First strings',ss[:60])
d=Path('work/SLPM_664.04').read_bytes(); shoff=struct.unpack_from('<I',d,32)[0]; sz,n,si=struct.unpack_from('<HHH',d,46)
sections=[struct.unpack_from('<10I',d,shoff+i*sz) for i in range(n)]
for sec in sections:
 if sec[1]==2:
  strs=sections[sec[6]]; st=d[strs[4]:strs[4]+strs[5]]; out=[]
  for o in range(sec[4],sec[4]+sec[5],sec[9]):
   name,v,s,info,other,idx=struct.unpack_from('<IIIBBH',d,o); name=st[name:].split(b'\0')[0].decode('ascii','replace');out.append(f'{v:08x} {s:6} {name}')
  Path('work/symbols.txt').write_text('\n'.join(out))
  print('Symbols',len(out));print('\n'.join(x for x in out if any(t in x.lower() for t in ['font','localized','amalg','text_parser','localiz'] ))[:16000])
