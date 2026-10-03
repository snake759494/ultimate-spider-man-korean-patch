"""Guard against reintroducing the per-panel caption clock and draw hook."""
from pathlib import Path
import struct,json

original=Path('work/SLPM_664.04').read_bytes()
patched=Path('build/runtime/SLPM_664.04').read_bytes()
symbols=json.loads(Path('build/runtime/symbols.json').read_text())
word=lambda data,off:struct.unpack_from('<I',data,off)[0]
assert word(original,0x1786a4)==0x0c09259e
assert word(patched,0x1786a4)==word(original,0x1786a4)
assert word(original,0x196c0c)==0x0c1632fb
assert word(patched,0x196c0c)==0x0c000000|(symbols['render_hook']>>2)
start=symbols['render_hook']-0xa0000+0x64a000
end=symbols['sound_hook']-0xa0000+0x64a000
code=struct.unpack('<'+'I'*((end-start)//4),patched[start:end])
calls=[(w&0x3ffffff)*4 for w in code if w>>26==3]
assert calls==[symbols['subtitle_frame'],0x58cbec],calls
report=dict(passed=True,per_panel_call_restored=True,
 overlay_hook_file_offset='0x196c0c',overlay_hook_virtual_address='0x295c0c',
 caption_update_before_final_overlay_scene_end=True,
 note='Static call-site/bridge regression check; runtime cadence must also be verified in PCSX2.')
Path('build/subtitle_hook_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
