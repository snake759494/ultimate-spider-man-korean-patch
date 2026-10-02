"""Exercise the real runtime logic with host-side sound/font bindings."""
from pathlib import Path
import subprocess,hashlib,json

out=Path('work/runtime_tests');out.mkdir(exist_ok=True)
source=Path('tools/subtitle_runtime.c').read_text()
replacements={
 '#include "subtitle_table.h"':'#include "fixture_table.h"',
 '*(void**)0x0069c9fc':'qa_font',
 '((u32(*)(u32))0x005cbf88)(source)':'qa_hash(source)',
 '((int(*)(void*,u32))0x005d1d40)((void*)0x006aa090,id)':'qa_lookup(id)',
 '*(u8**)0x006aa0bc':'qa_objects',
}
for old,new in replacements.items():
 assert source.count(old)==1,old
 source=source.replace(old,new)
(out/'fixture_table.h').write_text('''
typedef struct {unsigned short start,end,x1,x2;const char *line1,*line2;} Cue;
typedef struct {u32 hash;unsigned short first,count,duration,priority;} Clip;
static const Cue cues[]={{0,100,100,100,"test",""}};
static const Clip clips[]={
{1,0,1,120,2},{2,0,1,120,2},{3,0,1,120,2},{4,0,1,120,2},
{5,0,1,120,2},{6,0,1,120,2},{7,0,1,120,2},{8,0,1,120,2},
{9,0,1,120,1},{10,0,1,120,1},{11,0,1,120,1},{12,0,1,120,2}};
#define CLIP_COUNT 12
''')
prefix='''
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void *qa_font=(void*)1;
static unsigned qa_storage[16*48];
static unsigned char *qa_objects=(unsigned char*)qa_storage;
static unsigned qa_hash(unsigned source){return source;}
static int qa_lookup(unsigned id){return id<16?(int)id:-1;}
static unsigned qa_draws;
void draw_line(void *font,const char *s,unsigned color,unsigned x,unsigned y){qa_draws++;}
'''
tests='''
static unsigned char *object(unsigned i,unsigned hash) {
 unsigned char *p=qa_objects+i*192;
 memset(p,0,192);*(unsigned*)(p+0x8c)=hash;p[0x98]=4;return p;
}
static void reset(void) {
 memset(active,0,sizeof(active));memset(qa_storage,0,sizeof(qa_storage));
 frame_number=sound_count=captions_drawn=last_caption=qa_draws=0;
}
static unsigned count(void){unsigned n=0;for(unsigned i=0;i<8;i++)n+=active[i].clip!=0;return n;}
int main(void) {
 reset();subtitle_sound(object(0,999));assert(count()==0);
 for(unsigned i=0;i<8;i++){subtitle_sound(object(i,i+1));frame_number++;}
 assert(count()==8);subtitle_sound(object(8,9));
 for(unsigned i=0;i<8;i++)assert(active[i].clip->priority==2);
 subtitle_sound(object(9,12));assert(active[0].obj==qa_objects+9*192);
 reset();for(unsigned i=0;i<8;i++){subtitle_sound(object(i,9));frame_number++;}
 subtitle_sound(object(8,1));assert(active[0].clip->priority==2);
 subtitle_sound(object(1,10));assert(count()==8);assert(active[1].source==10);
 reset();unsigned char *p=object(0,1);p[0x98]=2;subtitle_sound(p);
 subtitle_frame();assert(active[0].ticks==0 && qa_draws==0);
 p[0x98]=4;subtitle_frame();assert(active[0].ticks==1 && qa_draws==5);
 *(unsigned short*)(p+0x96)=1;subtitle_frame();assert(active[0].ticks==1 && qa_draws==5);
 *(unsigned short*)(p+0x96)=0;p[0x98]=5;subtitle_frame();assert(active[0].ticks==1);
 p[0x98]=4;subtitle_frame();assert(active[0].ticks==2 && qa_draws==10);
 subtitle_stop(0);assert(count()==0);
 subtitle_sound(object(0,1));*(unsigned*)(qa_objects+0x8c)=2;subtitle_frame();assert(count()==0);
 subtitle_sound(object(0,1));active[0].ticks=121;subtitle_frame();assert(count()==0);
 p=object(0,1);p[0x98]=2;subtitle_sound(p);frame_number+=601;subtitle_frame();assert(count()==0);
 subtitle_stop(99);
 puts("PASS: priority, full queue, replacement, missing hash, loading, pause, resume, stop, source reuse, expiry");
}
'''
c=out/'runtime_test.c';c.write_text(prefix+source+tests)
exe=out/'runtime_test.exe'
subprocess.run(['work/compiler/ziglang/zig.exe','cc','-target','x86_64-windows-gnu','-O1',str(c),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
Path('build/runtime_tests.json').write_text(json.dumps(dict(
 passed=True,source_sha256=hashlib.sha256(Path('tools/subtitle_runtime.c').read_bytes()).hexdigest(),
 scope='Native host tests of actual runtime logic; these tests do not validate PS2 ABI or hardware',
 cases=['priority','full queue','replacement','missing hash','loading','pause','resume','stop','source reuse','expiry']
),indent=2))
