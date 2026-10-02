from pathlib import Path
import json,re,struct,numpy as np
from PIL import Image,ImageFont,ImageDraw
rows=json.loads(Path('translation/globaltext.json').read_text(encoding='utf-8'))
chars=sorted(set(c for r in rows for c in r['ko'] if ord(c)>127));p=bytearray(Path('work/packs/GAME.bin').read_bytes());fs=0x3de0;fz=31451
s=p[fs:fs+fz].decode('ascii').rstrip('\0');pat=r'(\d+) x (\d+) y (\d+) w (-?\d+) gx (-?\d+) gy (-?\d+) gw (\d+) gh (\d+)';recs=[list(map(int,m)) for m in re.findall(pat,s)];print('recs',len(recs),'chars',len(chars))
slots=[r for r in recs if r[0]>255 and 0xa0 not in r[0].to_bytes(2,'big') and r[7]>=16 and r[6]>=16];print('slots',len(slots))
assert len(slots)>=len(chars)
# Use original fixed atlas cells; reassign Japanese codepoints to Korean glyphs.
o=0xef880;h=o+128;pixstart=h+128;ims=131072;palette=np.frombuffer(p[pixstart+ims:pixstart+ims+128],np.uint8).reshape(-1,4)
b=np.frombuffer(p[pixstart:pixstart+ims],np.uint8);pix=np.empty(b.size*2,np.uint8);pix[::2]=b&15;pix[1::2]=b>>4;pix=pix.reshape(512,512)
font=ImageFont.truetype('NanumSquareNeo-cBd.ttf',17);mapping={}
for ch,rec in zip(chars,slots):
 code,x,y,w,gx,gy,gw,gh=rec;mapping[ch]=code
 pix[y:y+gh,x:x+gw]=2
 tile=Image.new('L',(gw,gh),0);dr=ImageDraw.Draw(tile);box=font.getbbox(ch);left=(gw-(box[2]-box[0]))//2;top=(gh-(box[3]-box[1]))//2
 dr.text((left-box[0],top-box[1]),ch,fill=255,font=font)
 arr=np.asarray(tile);lookup=np.array([int(np.argmin(abs(palette[:16,0].astype(int)-v))) for v in range(256)],np.uint8)
 # Transparent outside glyph; white with antialias luminance inside, original palette preserved.
 lookup[0]=2;lookup[1:]=np.array([3+int(np.argmin(abs(palette[3:16,0].astype(int)-v))) for v in range(1,256)],np.uint8)
 pix[y:y+gh,x:x+gw]=lookup[arr]
 # Fixed advance and baseline. Keep original cell bounds and original font parser text structure.
 rec[3]=17;rec[4]=0;rec[5]=0
new=s[:s.index('; char')]+ '; char bmofsx bmofsy cellwidth glyphofsx glyphofsy glyphwidth glyphheight\n'+''.join(f'{c} x {x} y {y} w {w} gx {gx} gy {gy} gw {gw} gh {gh}\n' for c,x,y,w,gx,gy,gw,gh in recs)
assert len(new.encode())+1<=fz
p[fs:fs+fz]=new.encode()+bytes(fz-len(new.encode()));flat=pix.ravel();p[pixstart:pixstart+ims]=(flat[::2]|(flat[1::2]<<4)).tobytes()
Path('build/GAME.bin').write_bytes(p);Path('translation/glyph_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
pal=palette.copy();pal[:,3]=np.minimum(pal[:,3].astype(int)*2,255);Image.fromarray(pal[pix],'RGBA').save('work/korean_font.png')
# Rewrite string pool only; preserve all original resource offsets and lengths.
p=bytearray(Path('work/packs/GLOBALTEXT_JAPANESE.bin').read_bytes());pool=bytearray();base=0x340;strbase=base+0xce0;end=0x7e1a
pattern=r'%[a-zA-Z]|~[a-zA-Z0-9_]+'
for r in rows:
 assert re.findall(pattern,r['jp'])==re.findall(pattern,r['ko']),(r['id'],'tokens')
 encoded=b''.join(mapping[c].to_bytes(2,'big') if c in mapping else c.encode('ascii') for c in r['ko'])
 struct.pack_into('<I',p,base+16+r['id']*4,len(pool));pool.extend(encoded+b'\0')
assert len(pool)<=end-strbase,(len(pool),end-strbase)
p[strbase:end]=pool+bytes(end-strbase-len(pool));Path('build/GLOBALTEXT_JAPANESE.bin').write_bytes(p)
print('font bytes',len(new),'text pool bytes',len(pool),'capacity',end-strbase)
