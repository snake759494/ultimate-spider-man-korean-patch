from pathlib import Path
p=Path('tools/build_resources.py');s=p.read_text(encoding='utf-8');s=s.replace("struct.pack_into('<II',p,0x688,0x2f00,31451)\nstruct.pack_into('<II',p,0x3f8,0xee9a0,0x20180)\nstruct.pack_into('<II',p,0x994,0x2018001,0xee9a0)\n",'');p.write_text(s,encoding='utf-8')
d=bytearray(Path('work/SLPM_664.04').read_bytes());assert d[0x606768:0x606776]==b'damnnoisykids\0';d[0x606768:0x606776]=b'arp12\0'+bytes(8);Path('build/SLPM_664.04').write_bytes(d)
p=Path('tools/build_iso.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("if name=='PACKS/AMALGA.PAK':", "if name in ['PACKS/AMALGA.PAK','SLPM_664.04']:");s=s.replace("Path('build/AMALGA.PAK').read_bytes()", "Path('build',Path(name).name).read_bytes()");p.write_text(s,encoding='utf-8')

