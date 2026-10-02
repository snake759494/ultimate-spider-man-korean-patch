from pathlib import Path
import json
texts={'5e892cf5':['잘 피해야겠어.'],'d1500246':['아야!','좀 더 빨리 피해야겠어!'],'941cdcdb':['에디, 이건 네 모습이 아니야.\n슈트가 널 조종하고 있어!']}
out=Path('translation/voice');out.mkdir(exist_ok=True)
for h,lines in texts.items():
 p=next(Path('work/voice_audio').rglob(h+'.review.json'));d=json.loads(p.read_text(encoding='utf-8'));assert len(lines)==len(d['segments'])
 for row,line in zip(d['segments'],lines):row['ko']=line
 d['status']='translated_from_medium_individual'
 (out/(h+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
