"""Reuse text only when decoded WAV files are byte-identical."""
from pathlib import Path
import hashlib,json
manifest=Path('work/duplicate_voice_audio.json')
if not manifest.exists():raise SystemExit('Missing exact-audio duplicate manifest')
count=0
for group in json.loads(manifest.read_text()):
 files=[Path(s) for s in group]
 available=[p for p in files if Path('translation/voice',p.stem+'.json').exists()]
 if not available:continue
 src=available[0];data=json.loads(Path('translation/voice',src.stem+'.json').read_text(encoding='utf-8'))
 source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
 for dst in files:
  target=Path('translation/voice',dst.stem+'.json')
  if target.exists():continue
  assert hashlib.sha256(dst.read_bytes()).hexdigest()==source_sha
  result=dict(data,hash=dst.stem,bank=dst.parent.name,identical_audio_source=src.stem,decoded_audio_sha256=source_sha)
  target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');count+=1
print('Byte-identical audio translations reused',count)
