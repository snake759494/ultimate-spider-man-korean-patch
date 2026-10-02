from pathlib import Path
import json
for line in Path('translation/voice_nonverbal.tsv').read_text(encoding='utf-8').splitlines():
 h,note=line.split('\t',1)
 files=list(Path('work/voice_audio').rglob(h+'.review.json'));assert len(files)==1,h
 d=json.loads(files[0].read_text(encoding='utf-8'))
 d['status']='no_caption_individual_asr_checked'
 d['review_note']=note+' 배치 및 개별 ASR 대조에 의한 분류이며 청취 검수와 구분.'
 for r in d['segments']:r['ko']=''
 Path('translation/voice',h+'.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
