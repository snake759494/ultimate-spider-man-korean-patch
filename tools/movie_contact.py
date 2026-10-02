from pathlib import Path
from PIL import Image,ImageDraw
files=list(Path('work/movies').glob('????????.png'));print(len(files));im=Image.new('RGB',(1024,((len(files)+3)//4)*245))
for i,f in enumerate(files):
 tile=Image.open(f).convert('RGB').resize((256,224));im.paste(tile,((i%4)*256,(i//4)*245));ImageDraw.Draw(im).text(((i%4)*256,(i//4)*245+224),f.stem,fill='white')
im.save('work/movie_samples.jpg')
