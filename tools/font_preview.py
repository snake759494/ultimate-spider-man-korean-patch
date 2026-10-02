from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import struct,numpy as np
p=Path('work/packs/GAME.bin').read_bytes();o=0xef880;h=o+128
size,cs,ims,hs,cc,fmt,mip,ct,it,w,ht=struct.unpack_from('<IIIHHBBBBHH',p,h)
print(size,cs,ims,hs,cc,fmt,mip,ct,it,w,ht)
a=np.frombuffer(p[h+hs:h+hs+ims],np.uint8);pix=np.empty(a.size*2,np.uint8);pix[::2]=a&15;pix[1::2]=a>>4
pal=np.frombuffer(p[h+hs+ims:h+hs+ims+cs],np.uint8).reshape(-1,4).copy();pal[:,3]=np.minimum(pal[:,3].astype(int)*2,255)
print(pal.tolist())
im=Image.fromarray(pal[pix.reshape(ht,w)],'RGBA');im.save('work/original_font.png')
