from pathlib import Path
import json
def load(h):return json.loads(Path('translation/scenes',h+'.json').read_text(encoding='utf-8'))
def save(h,d):Path('translation/scenes',h+'.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
# Early fragments disappear in an independent large-v3 pass and had high
# no-speech probability in the first pass. Keep them in the source audit only.
h='80892268';d=load(h)
for r in d['segments']:
 if r['start']<10:r['ko']='';r['review_note']='Unconfirmed non-speech fragment; omitted after second recognition pass.'
save(h,d)
h='4daf224d';d=load(h)
review=json.loads(Path('work/critical_review/sable_scene.json').read_text(encoding='utf-8'))
translations=['즉시 오스본에게 유전자 억제 장치를 채워라.','10초 안에 일대를 봉쇄해!','꾸물거리지 마!','퓨리의 부하들이야?','제법이군.','완전히 박살 낼 참이었는데.','나도 열심히 해 보긴 했어.','당신에 대해 조사했어.','이봐, 대신 일해 줬으면','좀 더 살갑게 대해 줘도 되잖아?']
assert len(review['segments'])==len(translations)
d['segments']=[dict(r,ko=ko) for r,ko in zip(review['segments'],translations)];save(h,d)
for h in ['c81b93b9','c81b93ba']:
 d=load(h)
 for r in d['segments']:r['ko']=r.get('ko','').replace('이모랑','숙모랑')
 save(h,d)
h='0d835571';d=load(h);d['segments'][7]['ko']='10분이면 가서 라이노를 때려눕히고,\n10분이면 돌아오겠네. 마스크를 거꾸로 써도 이기겠다.';save(h,d)
h='f71222d1';d=load(h);d['segments'][35]['ko']='저질러 줄 거야.';d['segments'][35]['review_note']='large-v3: しでかしてくれるだろう';save(h,d)
h='a754dbcf';d=load(h);d['segments'][5]['end']=22.05;save(h,d)
# Both independent recognizers retain the swimming metaphor. Peter explicitly
# asks what it means, so preserve that odd metaphor rather than invent a maxim.
h='f71222d1';d=load(h)
d['segments'][26]['ko']='밤 수영이다.'
d['segments'][36]['ko']='밤 수영이라고?'
save(h,d)
h='f71222d2';d=load(h);d['segments'][0]['ko']='밤 수영이라고? 자기가 뭔데 이래?';save(h,d)
