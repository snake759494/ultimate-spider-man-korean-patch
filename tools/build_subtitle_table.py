from pathlib import Path
import json,re,struct
mapping=json.loads(Path('translation/glyph_map_extended.json').read_text(encoding='utf-8'))
font=Path('build/GAME_extended.bin').read_bytes();off,size=struct.unpack_from('<II',font,0x678);base=struct.unpack_from('<I',font,0x1c)[0]
recs=re.findall(r'(\d+) x \d+ y \d+ w (-?\d+)',font[off+base:off+base+size].decode('ascii').rstrip('\0'))
widths={int(c):int(w) for c,w in recs}
def width(s):return sum(widths[mapping[c] if c in mapping else ord(c)] for c in s)
def wrap(s):
 lines=[]
 for para in s.split('\n'):
  line=''
  for word in para.split():
   test=(line+' '+word).strip()
   if width(test)>456 and line:lines.append(line);line=word
   else:line=test
   assert width(line)<=456,(s,line)
  if line:lines.append(line)
 return lines
def literal(s):
 data=b''.join(mapping[c].to_bytes(2,'big') if c in mapping else c.encode('ascii') for c in s)
 return '"'+''.join('\\x%02x'%b for b in data)+'"'
clips=[];cues=[];strings=[];report=[];line_ids={};line_references=0
for folder,priority in [('scenes',2),('voice',1)]:
 for p in sorted(Path('translation',folder).glob('*.json')):
  d=json.loads(p.read_text(encoding='utf-8'));start_idx=len(cues)
  for r in d['segments']:
   if not r.get('ko'):continue
   lines=wrap(r['ko']);groups=[lines[i:i+2] for i in range(0,len(lines),2)]
   weights=[sum(len(x) for x in g) for g in groups];total=sum(weights);duration=r['end']-r['start'];elapsed=0
   for group,weight in zip(groups,weights):
    a=round((r['start']+duration*elapsed/total)*30);elapsed+=weight;b=round((r['start']+duration*elapsed/total)*30)
    while len(group)<2:group.append('')
    ids=[]
    for line in group:
     if line not in line_ids:
      line_ids[line]=len(strings);strings.append(line)
     ids.append(line_ids[line]);line_references+=1
    # NGL uses a 640x448 logical viewport, displayed as 512x448 on this disc.
    cues.append((a,max(a+1,b),(640-width(group[0]))//2,(640-width(group[1]))//2,*ids))
  count=len(cues)-start_idx
  if count:clips.append((int(d['hash'],16),start_idx,count,round(d['duration']*30)+15,priority));report.append(dict(hash=d['hash'],cues=count,source=str(p)))
assert len(cues)<65536 and len({r[0] for r in clips})==len(clips)
assert all(0<=v<=65535 for row in clips for v in row[1:])
assert all(0<=v<=65535 for row in cues for v in row[:4])
header=['typedef struct {unsigned short start,end,x1,x2;const char *line1,*line2;} Cue;','typedef struct {u32 hash;unsigned short first,count,duration,priority;} Clip;']
for i,s in enumerate(strings):header.append(f'static const char text_{i}[]={literal(s)};')
header.append('static const Cue cues[]={'+','.join('{%d,%d,%d,%d,text_%d,text_%d}'%c for c in cues)+'};')
header.append('static const Clip clips[]={'+','.join('{0x%08x,%d,%d,%d,%d}'%c for c in sorted(clips))+'};')
header.append(f'#define CLIP_COUNT {len(clips)}')
Path('tools/subtitle_table.h').write_text('\n'.join(header)+'\n',encoding='ascii')
Path('build/subtitle_table.json').write_text(json.dumps(dict(clips=len(clips),cues=len(cues),unique_lines=len(strings),line_references=line_references,entries=report),indent=2))
print('subtitle clips',len(clips),'cues',len(cues),'unique lines',len(strings),'characters',sum(map(len,strings)))
