from pathlib import Path
import zipfile,zstandard,struct
def read(p):
 with zipfile.ZipFile(p) as z:
  r=z.getinfo('eeMemory.bin')
  with p.open('rb') as f:
   f.seek(r.header_offset);h=f.read(30);a,b=struct.unpack_from('<HH',h,26);f.seek(a+b,1);comp=f.read(r.compress_size)
  return zstandard.ZstdDecompressor().decompress(comp,max_output_size=r.file_size)
for crc in ['27CD1336','CBD34644']:
 p=next(Path('work/pcsx2/sstates').glob('*'+crc+'*.p2s'));d=read(p)
 ptr=struct.unpack_from('<I',d,0x69c9fc)[0]
 print(crc,'font',hex(ptr))
 vals=struct.unpack_from('<32I',d,ptr)
 print([(hex(i*4),hex(v)) for i,v in enumerate(vals)])
 for off in [0x24,0x28,0x2c,0x30,0x34,0x38]:
  v=vals[off//4]
  if 0x100000<v<len(d)-256:print(hex(off),hex(v),d[v:v+80].hex(' '))
 Path('work/ee_'+crc+'.bin').write_bytes(d)
