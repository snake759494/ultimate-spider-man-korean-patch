from pathlib import Path
p=Path('tools/build_resources.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("Path('build/GAME.bin').write_bytes(p)","struct.pack_into('<II',p,0x688,0x2f00,31451)\nstruct.pack_into('<II',p,0x3f8,0xee9a0,0x20180)\nstruct.pack_into('<II',p,0x994,0x2018001,0xee9a0)\nPath('build/GAME.bin').write_bytes(p)")
p.write_text(s,encoding='utf-8')
