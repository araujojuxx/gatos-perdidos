/* GATOS PERDIDOS - prototipo para Game Boy Advance (R36S / Miyoo Mini Plus via emulador GBA)
 * Sem bibliotecas: acessa os registradores do GBA direto. Compilar com devkitARM (veja LEIAME.md).
 * Controles: D-pad = andar | A = pular | START = voltar ao menu | L/R ou D-pad no menu = escolher gato
 */
#include "gfx.h"

typedef unsigned char u8; typedef signed int s32;

#define REG_DISPCNT (*(volatile u16*)0x04000000)
#define REG_VCOUNT  (*(volatile u16*)0x04000006)
#define REG_BG0CNT  (*(volatile u16*)0x04000008)
#define REG_BG0HOFS (*(volatile u16*)0x04000010)
#define REG_KEYINPUT (*(volatile u16*)0x04000130)
#define PAL_BG  ((volatile u16*)0x05000000)
#define PAL_OBJ ((volatile u16*)0x05000200)
#define CHARBLOCK0 ((volatile u32*)0x06000000)
#define SCRBLOCK28 ((volatile u16*)0x0600E000)
#define OBJ_VRAM ((volatile u32*)0x06010000)
#define OAM ((volatile u16*)0x07000000)

#define KEY_A 1
#define KEY_START 8
#define KEY_RIGHT 16
#define KEY_LEFT 32
#define KEY_R 256
#define KEY_L 512

#define GRAV 64
#define NPLAT (NCARS + NLEDGES)

static u16 oam_buf[128 * 4];
static int oam_n;

static void vsync(void) { while (REG_VCOUNT >= 160); while (REG_VCOUNT < 160); }

static void obj(int x, int y, int shape, int size, int tile, int pb, int hflip) {
    if (oam_n >= 128) return;
    u16 *o = &oam_buf[oam_n * 4];
    o[0] = (y & 0xFF) | (shape << 14);
    o[1] = (x & 0x1FF) | (hflip << 12) | (size << 14);
    o[2] = tile | (pb << 12);
    oam_n++;
}
static void oam_begin(void) { oam_n = 0; }
static void oam_end(void) {
    for (int i = oam_n; i < 128; i++) { oam_buf[i * 4] = 0x200; oam_buf[i * 4 + 1] = 0; oam_buf[i * 4 + 2] = 0; }
    for (int i = 0; i < 128 * 4; i++) OAM[i] = oam_buf[i];
}

static void load_gfx(void) {
    for (int i = 0; i < (int)(sizeof(spr_tiles) / 4); i++) OBJ_VRAM[i] = spr_tiles[i];
    for (int i = 0; i < (int)(sizeof(bg_tiles) / 4); i++) CHARBLOCK0[i] = bg_tiles[i];
    for (int i = 0; i < (int)(sizeof(bg_map) / 2); i++) SCRBLOCK28[i] = bg_map[i];
    for (int i = 0; i < 16; i++) {
        PAL_BG[i] = bg_pal[i];
        PAL_OBJ[0 * 16 + i] = pal_cat0[i];
        PAL_OBJ[1 * 16 + i] = pal_cat1[i];
        PAL_OBJ[2 * 16 + i] = pal_cat2[i];
        PAL_OBJ[3 * 16 + i] = pal_dog[i];
        PAL_OBJ[4 * 16 + i] = pal_car0[i];
        PAL_OBJ[5 * 16 + i] = pal_car1[i];
        PAL_OBJ[6 * 16 + i] = pal_heart[i];
    }
}

/* dados dos tres gatos: 0 Pudim, 1 Coitadinho, 2 Olaf */
static const s32 cat_speed[3] = { 384, 448, 320 };    /* 1.5 / 1.75 / 1.25 px por frame (x256) */
static const s32 cat_jump[3]  = { 1126, 1024, 1024 }; /* impulso do pulo */
static const int cat_hearts[3] = { 3, 3, 4 };         /* Olaf e o mais resistente */

/* plataformas: x, topo, largura, solido(carro=1 / sacada=0) */
static short plat[NPLAT][4];

static void build_platforms(void) {
    for (int i = 0; i < NCARS; i++) { plat[i][0] = cars[i][0]; plat[i][1] = GROUND - 13; plat[i][2] = 32; plat[i][3] = 1; }
    for (int i = 0; i < NLEDGES; i++) { int k = NCARS + i; plat[k][0] = ledges[i][0]; plat[k][1] = ledges[i][1]; plat[k][2] = ledges[i][2]; plat[k][3] = 0; }
}

static u16 keys, prev;
static void read_keys(void) { prev = keys; keys = ~REG_KEYINPUT & 0x3FF; }
static int pressed(int k) { return (keys & k) && !(prev & k); }

/* ---------------- menu de selecao ---------------- */
static int title(void) {
    static int sel = 0;
    int t = 0;
    REG_DISPCNT = 0x0000 | (1 << 12) | (1 << 6);   /* so sprites */
    PAL_BG[0] = (6 >> 0) | (6 << 5) | (14 << 10);
    for (;;) {
        vsync(); read_keys(); t++;
        if (pressed(KEY_LEFT) || pressed(KEY_L)) sel = (sel + 2) % 3;
        if (pressed(KEY_RIGHT) || pressed(KEY_R)) sel = (sel + 1) % 3;
        if (pressed(KEY_A) || pressed(KEY_START)) return sel;
        oam_begin();
        for (int i = 0; i < 3; i++) {
            int bounce = (i == sel) ? ((t >> 3) & 1) * 3 : 0;
            int pb = (i == 0) ? 0 : (i == 1) ? 1 : 2;
            obj(36 + i * 72, 76 - bounce, 0, 1, (i == sel && ((t >> 4) & 1)) ? TILE_CAT1 : TILE_CAT0, pb, 0);
        }
        obj(36 + sel * 72 + 4, 54 + ((t >> 3) & 1) * 2, 0, 0, TILE_HEART, 6, 0);
        oam_end();
    }
}

/* ---------------- jogo ---------------- */
typedef struct { s32 x; int dir; } Dog;

static int play(int cat) {
    REG_DISPCNT = 0x0000 | (1 << 8) | (1 << 12) | (1 << 6);
    REG_BG0CNT = (0 << 2) | (28 << 8) | (1 << 14);   /* charblock 0, screenblock 28, 64x32 */
    PAL_BG[0] = (3) | (4 << 5) | (10 << 10);

    s32 px = 8 * 256, py = (GROUND - 14) * 256, vx, vy = 0;
    int face = 0, onground = 1, hearts = cat_hearts[cat], inv = 0, anim = 0, chk = 0, won = 0, wint = 0;
    Dog d[NDOGS];
    for (int i = 0; i < NDOGS; i++) { d[i].x = dogs[i][0] * 256; d[i].dir = 1; }

    for (;;) {
        vsync(); read_keys();
        if (pressed(KEY_START)) return 0;

        if (!won) {
            s32 ox = px;
            if (keys & KEY_LEFT) { vx = -cat_speed[cat]; face = 1; }
            else if (keys & KEY_RIGHT) { vx = cat_speed[cat]; face = 0; }
            else vx = 0;
            px += vx;
            if (px < 0) px = 0;
            if (px > (WORLD - 16) * 256) px = (WORLD - 16) * 256;
            int fx = px >> 8, feet = (py >> 8) + 14;
            for (int i = 0; i < NPLAT; i++) {          /* parede dos carros */
                if (!plat[i][3]) continue;
                if (fx + 12 > plat[i][0] && fx + 4 < plat[i][0] + plat[i][2] && feet > plat[i][1] + 2) { px = ox; break; }
            }
            if (onground && pressed(KEY_A)) { vy = -cat_jump[cat]; onground = 0; }
            vy += GRAV; if (vy > 1024) vy = 1024;
            int oldfeet = (py >> 8) + 14;
            py += vy;
            int newfeet = (py >> 8) + 14;
            fx = px >> 8;
            onground = 0;
            if (vy >= 0) {
                int best = 9999;
                for (int i = 0; i < NPLAT; i++) {
                    int t = plat[i][1];
                    if (fx + 12 > plat[i][0] && fx + 4 < plat[i][0] + plat[i][2] && oldfeet <= t && newfeet >= t && t < best) best = t;
                }
                if (newfeet >= GROUND && best > GROUND) best = GROUND;
                if (best != 9999) { py = (best - 14) * 256; vy = 0; onground = 1; }
            }
            if (onground) { int c = (fx / 128) * 128; if (c > chk) chk = c; }

            /* cachorros */
            if (inv > 0) inv--;
            feet = (py >> 8) + 14;
            for (int i = 0; i < NDOGS; i++) {
                d[i].x += d[i].dir * 192;
                if ((d[i].x >> 8) >= dogs[i][1]) d[i].dir = -1;
                if ((d[i].x >> 8) <= dogs[i][0]) d[i].dir = 1;
                int dx = (d[i].x >> 8) - fx;
                if (dx < 11 && dx > -11 && feet > GROUND - 8 && inv == 0) {
                    hearts--; inv = 120;
                    if (hearts <= 0) { hearts = cat_hearts[cat]; chk = 0; }
                    px = (chk + 8) * 256; py = (GROUND - 14) * 256; vy = 0;
                }
            }
            if ((px >> 8) >= WORLD - 40) won = 1;
        } else {
            wint++;
            if (wint > 30 && pressed(KEY_A)) return 0;
            PAL_BG[0] = (30) | (20 << 5) | (12 << 10);   /* amanhecer: chegou em casa! */
        }

        int cam = (px >> 8) - 100;
        if (cam < 0) cam = 0;
        if (cam > WORLD - 240) cam = WORLD - 240;
        REG_BG0HOFS = cam;

        oam_begin();
        for (int i = 0; i < NCARS; i++) {
            int sx = cars[i][0] - cam;
            if (sx > -32 && sx < 240) obj(sx, GROUND - 16, 1, 1, TILE_CAR, 4 + cars[i][1], 0);
        }
        for (int i = 0; i < NDOGS; i++) {
            int sx = (d[i].x >> 8) - cam;
            if (sx > -16 && sx < 240) obj(sx, GROUND - 14, 0, 1, ((d[i].x >> 11) & 1) ? TILE_DOG1 : TILE_DOG0, 3, d[i].dir < 0);
        }
        if (!(inv > 0 && ((inv >> 2) & 1))) {
            if (vx != 0 && onground) anim++;
            int fr = (!onground) ? 1 : ((anim >> 3) & 1);
            int sy = (py >> 8) - (won ? ((wint >> 3) & 1) * 3 : 0);
            obj((px >> 8) - cam, sy, 0, 1, fr ? TILE_CAT1 : TILE_CAT0, cat, face);
        }
        for (int i = 0; i < hearts; i++) obj(4 + i * 10, 4, 0, 0, TILE_HEART, 6, 0);
        if (won) for (int i = 0; i < 5; i++) obj((px >> 8) - cam - 24 + i * 12, 40 + ((wint + i * 5) % 40), 0, 0, TILE_HEART, 6, 0);
        oam_end();
    }
}

int main(void) {
    load_gfx();
    build_platforms();
    for (;;) { int c = title(); play(c); }
    return 0;
}
