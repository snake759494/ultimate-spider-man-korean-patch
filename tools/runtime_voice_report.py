from pathlib import Path
import json
inventory=json.loads(Path('work/audio_inventory.json').read_text());index={}
for bank in inventory:
 for i,s in enumerate(bank['streams']):index[f"{s['hash']:08x}"]=(bank['name'],i,s['duration'])
ev=json.loads(Path('work/runtime_events.json').read_text());seen=set()
for e in sorted(ev['events'],key=lambda e:e['frame']):
 h=e['hash']
 if h in seen:continue
 seen.add(h);bank,i,d=index.get(h,('',0,0))
 if 'VOICE' in bank or 'SCENE' in bank or 'MISC' in bank:print(h,bank,i,d)
