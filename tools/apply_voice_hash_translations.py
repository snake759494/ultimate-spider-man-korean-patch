from pathlib import Path
import json
out=Path('translation/voice')
for line in Path('translation/voice_by_hash.tsv').read_text(encoding='utf-8').splitlines():
 h,ko=line.split('\t');target=out/(h+'.json')
 if target.exists() and json.loads(target.read_text(encoding='utf-8')).get('status') in ('translated_from_individual_asr_context_checked','translated_from_medium_batch_context_checked_audio_review_required','translated_from_kotoba_batch_context_checked_audio_review_required'):continue
 p=next(Path('work/voice_audio').rglob(h+'.json'))
 d=json.loads(p.read_text(encoding='utf-8'));assert len(d['segments'])==1,h
 d['segments'][0]['ko']=ko;d['status']='translated_text_reviewed_audio_review_required'
 target.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
