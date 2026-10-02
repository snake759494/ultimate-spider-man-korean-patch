typedef unsigned int u32;
typedef unsigned char u8;
extern void draw_line(void*,const char*,u32,u32,u32);
volatile u32 frame_number;
volatile u32 sound_count;
volatile u32 captions_drawn;
volatile u32 last_caption;
volatile u32 sounds[768];
#include "subtitle_table.h"
typedef struct {const Clip *clip;u8 *obj;u32 source,ticks,stamp;} Active;
static Active active[8];
static u32 float_bits(u32 n) {
    if (!n) return 0;
    u32 e=0,v=n;while(v>>=1)e++;
    return ((e+127)<<23)|((n<<(23-e))&0x7fffff);
}
static void outlined(void *font,const char *s,u32 x,u32 y) {
    if (!*s) return;
    draw_line(font,s,0x80000000,float_bits(x-1),float_bits(y));
    draw_line(font,s,0x80000000,float_bits(x+1),float_bits(y));
    draw_line(font,s,0x80000000,float_bits(x),float_bits(y-1));
    draw_line(font,s,0x80000000,float_bits(x),float_bits(y+1));
    draw_line(font,s,0x80ffffff,float_bits(x),float_bits(y));
}
void subtitle_frame(void) {
    void *font=*(void**)0x0069c9fc;
    const Cue *chosen=0;u32 priority=0,stamp=0;
    frame_number++;
    for(u32 i=0;i<8;i++) {
        Active *a=&active[i];if(!a->clip)continue;
        if(*(u32*)(a->obj+0x8c)!=a->source || a->ticks>a->clip->duration) {a->clip=0;continue;}
        if(*(unsigned short*)(a->obj+0x96) || a->obj[0x98]==5)continue;
        /* States 1..3 prepare the stream; state 4 starts the audio clock. */
        if(a->obj[0x98]!=4) {
            if(frame_number-a->stamp>600)a->clip=0;
            continue;
        }
        u32 t=a->ticks++;
        for(u32 j=0;j<a->clip->count;j++) {
            const Cue *c=&cues[a->clip->first+j];
            if(t>=c->start && t<c->end && (a->clip->priority>priority || (a->clip->priority==priority && a->stamp>=stamp))) {
                chosen=c;priority=a->clip->priority;stamp=a->stamp;
            }
        }
    }
    if(!font || !chosen)return;
    captions_drawn++;last_caption=(u32)chosen;
    outlined(font,chosen->line1,chosen->x1,chosen->line2[0]?306:326);
    outlined(font,chosen->line2,chosen->x2,326);
}
void subtitle_stop(u32 id) {
    int idx=((int(*)(void*,u32))0x005d1d40)((void*)0x006aa090,id);
    if(idx<0)return;
    u8 *obj=*(u8**)0x006aa0bc+idx*192;
    for(u32 i=0;i<8;i++)if(active[i].obj==obj)active[i].clip=0;
}
void subtitle_sound(void *obj) {
    u32 source=*(u32*)((u8*)obj+0x8c);
    u32 hash=((u32(*)(u32))0x005cbf88)(source);
    u32 i=sound_count++ % 256;
    sounds[i*3]=hash;
    sounds[i*3+1]=frame_number;
    sounds[i*3+2]=source;
    u32 lo=0,hi=CLIP_COUNT;
    while(lo<hi) {u32 mid=(lo+hi)/2;if(clips[mid].hash<hash)lo=mid+1;else hi=mid;}
    if(lo==CLIP_COUNT || clips[lo].hash!=hash)return;
    u32 slot=0,available=0;
    for(i=0;i<8;i++) {
        if(!active[i].clip || active[i].obj==obj) {slot=i;available=1;break;}
        if(active[i].clip->priority<active[slot].clip->priority ||
           (active[i].clip->priority==active[slot].clip->priority && active[i].stamp<active[slot].stamp))slot=i;
    }
    /* Crowded streets must not evict story dialogue with a lower-priority bark. */
    if(!available && clips[lo].priority<active[slot].clip->priority)return;
    active[slot].clip=&clips[lo];active[slot].obj=obj;active[slot].source=source;
    active[slot].ticks=0;active[slot].stamp=frame_number;
}
