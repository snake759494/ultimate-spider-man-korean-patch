from pathlib import Path
import json
source=Path('work/cinematics/asr_medium/S01_FAPR_IGC1_JP.json')
d=json.loads(source.read_text(encoding='utf-8'))
ko=['모든 일은 이렇게 시작됐어.','지금 이 황당한 상황은 그 결과지.','몇 달 전, 어린 시절 친구인 에디 브록과 다시 만났어.','대대로 이어지는 거야.','에디의 아버지와 우리 아버지는 함께 일하셨어.','돌아가시기 전까지는.','이 슈트가 마지막 열쇠가 될 거라고 생각한다.','마침내 암 치료법을 완성하는 거야.','난 그저 세상에서 죽어 가는 사람들을 돕고 싶을 뿐이야.','하지만 그 계약서에 서명하는 바람에...','그것조차 할 수 없게 됐어.','놈들이 아버지에게서 슈트를 빼앗았어.','내가 되찾을 거야.','아버지가 시작한 일을 내가 끝내겠어.','정말 기분이 좋았어.','내가 훨씬 강해진 것 같았지.','아주 잠깐이었지만.','간신히 목숨을 건졌어.','슈트가 어떻게 된 건지, 내 몸에 무슨 짓을 한 건지는 몰라.','하지만 스파이더맨조차 통제 못 한다면 누가 할 수 있겠어?','그런데 내가 한 일과 내 정체를 알게 된 에디는...','몹시 화가 났지.']
assert len(ko)==len(d['segments'])
for r,k in zip(d['segments'],ko):r['ko']=k
d['video_hash']='88dd1e5f';d['review']='Japanese ASR cross-check; timing and in-game playback require visual verification'
Path('translation/cinematics').mkdir(exist_ok=True)
Path('translation/cinematics/S01_FAPR_IGC1_JP.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
