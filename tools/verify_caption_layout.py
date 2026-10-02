"""Check real atlas glyph extents and render long two-line caption proofs."""
from pathlib import Path
import json,re,struct
from PIL import Image,ImageDraw
import build_subtitle_table as table

game=Path('build/GAME_extended.bin').read_bytes();base=struct.unpack_from('<I',game,0x1c)[0]
off,size=struct.unpack_from('<II',game,0x678)
recs={int(r[0]):tuple(map(int,r[1:])) for r in re.findall(r'(\d+) x (\d+) y (\d+) w (-?\d+) gx (-?\d+) gy (-?\d+) gw (\d+) gh (\d+)',game[base+off:base+off+size].decode('ascii'))}
atlas=Image.open('work/korean_font_extended.png').convert('RGBA')
proofs=[];checked=0
for folder in ('scenes','voice'):
 for p in Path('translation',folder).glob('*.json'):
  d=json.loads(p.read_text(encoding='utf-8'))
  for r in d['segments']:
   if not r.get('ko'):continue
   lines=table.wrap(r['ko'])
   for i in range(0,len(lines),2):
    group=lines[i:i+2];extent=0
    for line in group:
     x=(640-table.width(line))//2
     for c in line:
      _,_,advance,gx,gy,gw,gh=recs[table.mapping.get(c,ord(c))]
      assert x+gx>=0 and x+gx+gw<=640,(p,line,c,x,gx,gw)
      assert 20+gy>=0 and 20+gy+gh<=60,(p,line,c,gy,gh)
      extent=max(extent,x+gx+gw);x+=advance
     checked+=1
    proofs.append((max(table.width(x) for x in group),d['hash'],group))
proofs.sort(reverse=True);selected=[];seen=set()
for _,h,group in proofs:
 if tuple(group) in seen:continue
 seen.add(tuple(group));selected.append((h,group))
 if len(selected)==20:break
sheet=Image.new('RGBA',(1280,1100),(24,28,35,255));draw=ImageDraw.Draw(sheet)
for i,(h,group) in enumerate(selected):
 ox=i%2*640;oy=i//2*110;draw.text((ox+16,oy+7),f'{h} / atlas proof / logical 640 px',fill='white')
 draw.rectangle((ox+90,oy+32,ox+550,oy+88),outline=(70,80,96,255))
 for j,line in enumerate(group):
  x=ox+(640-table.width(line))//2;y=oy+40+j*20
  for c in line:
   tx,ty,advance,gx,gy,gw,gh=recs[table.mapping.get(c,ord(c))]
   sheet.alpha_composite(atlas.crop((tx,ty,tx+gw,ty+gh)),(x+gx,y+gy));x+=advance
sheet.convert('RGB').save('build/caption_layout_proof.png')
Path('build/caption_layout_verification.json').write_text(json.dumps(dict(lines_checked=checked,all_glyphs_within_viewport=True,proof_samples=len(selected),note='Atlas/layout proof; gameplay background contrast and scene timing require runtime review.'),indent=2),encoding='utf-8')
print('PASS: actual atlas bounds for',checked,'caption lines')
