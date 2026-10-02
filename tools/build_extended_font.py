from pathlib import Path
import json,re,struct,sys
import numpy as np
from PIL import Image,ImageFont,ImageDraw
from font_outline import outlined_glyph

p=bytearray(Path('work/packs/GAME.bin').read_bytes())
original_size=len(p)
mapping=json.loads(Path('translation/glyph_map.json').read_text(encoding='utf-8'))
chars=set(mapping)
for cp in range(0xac00,0xd7a4) if '--all' in sys.argv else []:
 try: chr(cp).encode('euc_kr')
 except UnicodeEncodeError: continue
 else:
  if len(chr(cp).encode('euc_kr'))==2:chars.add(chr(cp))
if '--all' not in sys.argv:
 for path in [*Path('translation/scenes').glob('*.json'),*Path('translation/voice').glob('*.json')]:
  data=json.loads(path.read_text(encoding='utf-8'))
  for row in data['segments']:chars.update(c for c in row.get('ko','') if ord(c)>127)
width=1024;height=1024;cell=20;cols=width//cell
used=set(mapping.values())
codes=(a*256+b for a in list(range(0x81,0xa0))+list(range(0xe0,0xf0)) for b in range(0x40,0xfd) if b not in (0x7f,0xa0) and a*256+b not in used)
for c in sorted(chars):
 if c not in mapping:mapping[c]=next(codes)
s=p[0x3de0:0x3de0+31451].decode('ascii').rstrip('\0')
recs=[list(map(int,m)) for m in re.findall(r'(\d+) x (\d+) y (\d+) w (-?\d+) gx (-?\d+) gy (-?\d+) gw (\d+) gh (\d+)',s)]
ascii_recs=[r for r in recs if r[0]<=255]
assert len(ascii_recs)+len(mapping)<=cols*(height//cell)
oldtex=bytes(p[0xef880:0xef880+131456]);b=np.frombuffer(oldtex[256:256+131072],np.uint8)
old=np.empty(b.size*2,np.uint8);old[::2]=b&15;old[1::2]=b>>4;old=old.reshape(512,512)
pal=np.frombuffer(oldtex[-128:],np.uint8).reshape(-1,4)
pix=np.zeros((height,width),np.uint8);outrecs=[]
for i,r in enumerate(ascii_recs):
 c,x,y,w,gx,gy,gw,gh=r;nx=i%cols*cell;ny=i//cols*cell
 pix[ny:ny+gh,nx:nx+gw]=old[y:y+gh,x:x+gw]
 outrecs.append([c,nx,ny,w,gx,gy,gw,gh])
font=ImageFont.truetype('NanumSquareNeo-cBd.ttf',17)
for i,(ch,c) in enumerate(sorted(mapping.items(),key=lambda t:t[1]),len(ascii_recs)):
 x=i%cols*cell;y=i//cols*cell
 pix[y:y+20,x:x+20]=outlined_glyph(ch,font,pal)
 # Preserve the original face position and 17-pixel advance after padding.
 outrecs.append([c,x,y,17,-1,-1,20,20])
header=s[:s.index('; char')]
header=re.sub(r'numgood\s+\d+',f'numgood {len(outrecs)}',header)
# The parser uses the original header keyword, verified below.
print(header)
fdf=(header+'; char bmofsx bmofsy cellwidth glyphofsx glyphofsy glyphwidth glyphheight\n'+''.join(f'{c} x {x} y {y} w {w} gx {gx} gy {gy} gw {gw} gh {gh}\n' for c,x,y,w,gx,gy,gw,gh in sorted(outrecs))+'\0').encode()
tex=bytearray(oldtex[:256]);flat=pix.ravel();tex.extend((flat[::2]|flat[1::2]<<4).tobytes());tex.extend(oldtex[-128:])
pixels=width*height//2
struct.pack_into('<III',tex,128,128+pixels+128,128,pixels)
struct.pack_into('<HH',tex,148,width,height)
gs=struct.unpack_from('<Q',tex,152)[0];gs=(gs&~((15<<26)|(15<<30)))|((width.bit_length()-1)<<26)|((height.bit_length()-1)<<30);struct.pack_into('<Q',tex,152,gs)
def append(data):
 p.extend(bytes((-len(p))%128));off=len(p);p.extend(data);return off-0xee0
fo=append(fdf);to=append(tex);p.extend(bytes((-len(p))%128))
# Allocation descriptors point beyond the decompressed file into its auxiliary
# arena. Move that arena past the newly appended resources as well.
for pos in range(0xe78,0xedc,12):
 old=struct.unpack_from('<I',p,pos)[0]
 assert original_size<=old<original_size+0x6000,(hex(pos),hex(old))
 struct.pack_into('<I',p,pos,old+len(p)-original_size)
struct.pack_into('<II',p,0x670+8,fo,len(fdf))
struct.pack_into('<II',p,0x390+8,to,len(tex))
struct.pack_into('<II',p,0x93c+4,(len(tex)<<8)|1,to)
# A 1024-square TIM2 needs a 368-byte aligned upload packet. The original
# cooked allocation pools only provide the packet sizes used by its assets.
if width==1024 and height==1024:
 pools=[list(struct.unpack_from('<III',p,pos)) for pos in range(0xe70,0xedc,12)]
 p[0xee0:0xee0]=bytes(128)
 for row in pools:row[2]+=128
 pools.append([0x00800170,0x00060001,len(p)+0x6000])
 pools.sort(key=lambda r:r[0]&0xffff,reverse=True)
 for i,row in enumerate(pools):struct.pack_into('<III',p,0xe70+i*12,*row)
 struct.pack_into('<I',p,0xb4,0x01000000|len(pools))
 struct.pack_into('<I',p,0x1c,0xf60)
 struct.pack_into('<I',p,0x38,0xf30)
 struct.pack_into('<I',p,0x28,0x7000)
Path('build/GAME_extended.bin').write_bytes(p)
Path('translation/glyph_map_extended.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
rgba=pal.copy();rgba[:,3]=np.minimum(rgba[:,3].astype(int)*2,255)
Image.fromarray(rgba[pix],'RGBA').save('work/korean_font_extended.png')
print('glyphs',len(outrecs),'font',len(fdf),'texture',len(tex),'GAME',len(p))
