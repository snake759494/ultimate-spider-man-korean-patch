from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(1100,610),'#202020');dr=ImageDraw.Draw(im)
orig=Image.open('work/original_font.png').convert('RGB');im.paste(orig.crop((0,118,500,158)).resize((1000,80)),(40,20))
for i,f in enumerate(Path('.').glob('*.ttf')):
 font=ImageFont.truetype(str(f),17);label=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
 dr.text((20,120+i*51),f.stem,fill='white',font=label)
 tile=Image.new('RGB',(380,23),'black');ImageDraw.Draw(tile).text((0,-1),'게임을 저장합니다. 스파이더맨 이동 전투',font=font,fill='white');im.paste(tile.resize((760,46)),(330,110+i*51))
im.save('work/font_comparison.png')
