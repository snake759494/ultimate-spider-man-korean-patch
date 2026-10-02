from pathlib import Path
import json,re
rows=[]
for p in Path('work/voice_audio/STREAMS_VOICE_JP').glob('*.json'):
 if p.name.endswith('.review.json') or Path('translation/voice',p.name).exists():continue
 d=json.loads(p.read_text(encoding='utf-8'));a=''.join(s['jp'] for s in d['segments'])
 rp=p.with_suffix('.review.json'); b=''
 if rp.exists():b=''.join(s['jp'] for s in json.loads(rp.read_text(encoding='utf-8'))['segments'])
 if max(len(a),len(b))>=10:rows.append((max(len(a),len(b)),p.stem,a,b))
rows.sort(reverse=True)
Path('work/remaining_bilingual_asr.txt').write_text('\n'.join(f'{h}\t{a}\t{b}' for _,h,a,b in rows),encoding='utf-8')
print(len(rows));print('\n'.join(f'{h}\t{a}\t{b}' for _,h,a,b in rows[:85]))
