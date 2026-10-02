"""Verify the packed font has a complete black rim without moving its face."""
from pathlib import Path
import json,re,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter

game=Path('build/GAME_extended.bin').read_bytes()
base=struct.unpack_from('<I',game,0x1c)[0]
off,size=struct.unpack_from('<II',game,0x678)
records={int(r[0]):list(map(int,r[1:])) for r in re.findall(
 r'(\d+) x (\d+) y (\d+) w (-?\d+) gx (-?\d+) gy (-?\d+) gw (\d+) gh (\d+)',
 game[base+off:base+off+size].decode('ascii'))}
off,size=struct.unpack_from('<II',game,0x398)
tex=game[base+off:base+off+size]
packed=np.frombuffer(tex[256:-128],np.uint8)
pixels=np.empty(packed.size*2,np.uint8)
pixels[::2]=packed&15;pixels[1::2]=packed>>4
pixels=pixels.reshape(1024,1024)
palette=np.frombuffer(tex[-128:],np.uint8).reshape(-1,4)
mapping=json.loads(Path('translation/glyph_map_extended.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('NanumSquareNeo-cBd.ttf',17)
for ch,code in mapping.items():
 x,y,advance,gx,gy,w,h=records[code]
 assert (advance,gx,gy,w,h)==(17,-1,-1,20,20)
 face=Image.new('L',(20,20));b=font.getbbox(ch)
 ImageDraw.Draw(face).text((1+(18-b[2]+b[0])//2-b[0],1+(18-b[3]+b[1])//2-b[1]),ch,font=font,fill=255)
 coverage=np.asarray(face)
 expanded=np.asarray(face.point(lambda v:255 if v else 0).filter(ImageFilter.MaxFilter(3)))>0
 tile=pixels[y:y+h,x:x+w]
 assert np.all(tile[expanded & (coverage==0)]==3),ch
 assert np.all(tile[~expanded]==0),ch
 assert not np.any(tile==2),ch
 assert tuple(palette[3])==(0,0,0,120)  # Original PS2 alpha (0x80 = 100%).
 # The face's old luminance mapping is unchanged, so only the rim is added.
 lookup=np.array([3+np.argmin(abs(palette[3:16,0].astype(int)-v)) for v in range(256)])
 assert np.all(tile[coverage>0]==lookup[coverage[coverage>0]]),ch

atlas=Image.open('work/korean_font_extended.png').convert('RGBA')
oldgame=Path('work/GAME_before_outline.bin').read_bytes()
oldbase=struct.unpack_from('<I',oldgame,0x1c)[0];o,n=struct.unpack_from('<II',oldgame,0x678)
oldrecords={int(r[0]):list(map(int,r[1:])) for r in re.findall(
 r'(\d+) x (\d+) y (\d+) w (-?\d+) gx (-?\d+) gy (-?\d+) gw (\d+) gh (\d+)',oldgame[oldbase+o:oldbase+o+n].decode('ascii'))}
oldatlas=Image.open('work/korean_font_before_outline.png').convert('RGBA')
sheet=Image.new('RGBA',(640,240),(175,185,130,255));draw=ImageDraw.Draw(sheet)
for row,(label,source,recs) in enumerate([('BEFORE',oldatlas,oldrecords),('AFTER: opaque black outline',atlas,records)]):
 oy=row*120;draw.text((20,oy+12),label,fill='black')
 for j,line in enumerate(['스파이더 센스가 발동하면','버튼을 길게 눌러 위험을 피해라!','점프해서 올라가면 돼. 간단하지.']):
  x=30;y=oy+35+j*24
  for ch in line:
   tx,ty,a,gx,gy,w,h=recs[mapping.get(ch,ord(ch))]
   sheet.alpha_composite(source.crop((tx,ty,tx+w,ty+h)),(x+gx,y+gy));x+=a
sheet.convert('RGB').resize((1280,480),Image.Resampling.NEAREST).save('build/font_outline_comparison.png')
report=dict(hangul_glyphs_checked=len(mapping),complete_black_rim=True,outline_pixels=1,
 transparent_background_index=0,opaque_black_index=3,face_luminance_and_position_preserved=True,
 advance_pixels=17,ascii_glyphs_unchanged=True)
for code,r in oldrecords.items():
 if code>255:continue
 x,y,a,gx,gy,w,h=records[code];ox,oy,oa,ogx,ogy,ow,oh=r
 assert (a,gx,gy,w,h)==(oa,ogx,ogy,ow,oh)
 assert atlas.crop((x,y,x+w,y+h)).tobytes()==oldatlas.crop((ox,oy,ox+w,oy+oh)).tobytes()
Path('build/font_outline_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
