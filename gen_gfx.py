#!/usr/bin/env python3
"""Gera gfx.h (sprites, tiles, paleta, mapa e fase) para o jogo Gatos Perdidos (GBA).
Edite as paletas / pixel art / fase aqui e rode:  python3 gen_gfx.py"""
import random

def rgb15(r, g, b):
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)

def pal(colors):
    p = [0] * 16
    for i, c in enumerate(colors):
        p[i] = rgb15(*c)
    return p

# ---------- pixel art 16x16 (indices: 0 vazio, 1 contorno, 2 cor principal, 3 cor secundaria, 4 olho, 5 nariz)
def pad(rows):
    out = []
    for r in rows:
        assert len(r) <= 16, r
        out.append(r.ljust(16, '.'))
    while len(out) < 16:
        out.append('.' * 16)
    return out

CAT0 = pad([
    "",
    "...........1..1.",
    "..........121121",
    "..........122221",
    "..........142421",
    "..........122521",
    "..1...1111222221",
    ".1.1122222222221",
    "..1122323232321.",
    "..1122222222221.",
    "...111111111111.",
    "...1.1....1.1...",
    "...1.1....1.1...",
    "..11.11..11.11..",
])
CAT1 = pad([
    "",
    "...........1..1.",
    "..........121121",
    "..........122221",
    "..........142421",
    "..........122521",
    "..1...1111222221",
    ".1.1122222222221",
    "..1122323232321.",
    "..1122222222221.",
    "...111111111111.",
    "....11....11....",
    "...1..1..1..1...",
    "..11..11.11..11.",
])
DOG0 = pad([
    "",
    "",
    "..........11....",
    ".........1221...",
    "..1.....11222211",
    ".121..1112222421",
    "..12111222222221",
    "..1222222222211.",
    "..1223322223311.",
    "..1222222222211.",
    "..1222222222211.",
    "...11111111111..",
    "...1.1....1.1...",
    "...1.1....1.1...",
    "..11.11..11.11..",
])
DOG1 = pad([
    "",
    "",
    "..........11....",
    ".........1221...",
    "..1.....11222211",
    ".121..1112222421",
    "..12111222222221",
    "..1222222222211.",
    "..1223322223311.",
    "..1222222222211.",
    "..1222222222211.",
    "...11111111111..",
    "....11....11....",
    "...1..1..1..1...",
    "..11..11.11..11.",
])
HEART = [
    "........",
    ".11..11.",
    "1221122 1".replace(" ", ""),
    "12222221",
    "12222221",
    ".122221.",
    "..1221..",
    "...11...",
]
HEART = [r[:8].ljust(8, '.') for r in HEART]

def make_car():
    w, h = 32, 16
    g = [['.'] * w for _ in range(h)]
    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1):
            for x in range(x0, x1):
                g[y][x] = c
    rect(0, 7, 32, 13, '1')          # contorno corpo
    rect(1, 8, 31, 12, '2')          # corpo
    rect(6, 3, 26, 8, '1')           # cabine contorno
    rect(7, 4, 25, 8, '2')
    rect(9, 4, 15, 7, '3')           # vidros
    rect(17, 4, 23, 7, '3')
    rect(0, 10, 2, 11, '4')          # farol
    rect(30, 10, 32, 11, '4')
    for cx in (7, 22):               # rodas
        rect(cx, 12, cx + 5, 16, '1')
        rect(cx + 1, 13, cx + 4, 15, '5')
    return [''.join(r) for r in g]
CAR = make_car()

def tiles_from_grid(grid, w, h):
    """Converte grade de caracteres numa lista de tiles 8x8 4bpp na ordem do modo 1D (linha a linha)."""
    out = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            for y in range(8):
                v = 0
                for x in range(8):
                    c = grid[ty * 8 + y][tx * 8 + x]
                    n = 0 if c == '.' else int(c)
                    v |= n << (4 * x)
                out.append(v)
    return out

# ---------- paletas dos sprites (0 = transparente)
PAL_CAT = [
    # Pudim: branco e bege, olhos verdes
    pal([(0, 0, 0), (110, 80, 60), (250, 246, 238), (222, 190, 150), (60, 170, 90), (240, 150, 160)]),
    # Coitadinho: preto, olhos amarelos
    pal([(0, 0, 0), (8, 8, 12), (38, 38, 48), (78, 78, 96), (255, 220, 40), (200, 120, 130)]),
    # Olaf: branco e cinza, olhos azuis
    pal([(0, 0, 0), (70, 74, 86), (242, 242, 246), (150, 154, 166), (70, 150, 230), (240, 150, 160)]),
]
PAL_DOG = pal([(0, 0, 0), (50, 28, 14), (150, 96, 52), (110, 66, 34), (255, 255, 255)])
PAL_CAR_RED = pal([(0, 0, 0), (30, 20, 30), (190, 40, 50), (130, 170, 210), (255, 230, 120), (20, 20, 24)])
PAL_CAR_BLUE = pal([(0, 0, 0), (20, 24, 40), (50, 90, 190), (130, 170, 210), (255, 230, 120), (20, 20, 24)])
PAL_HEART = pal([(0, 0, 0), (90, 10, 30), (240, 60, 90)])

# ---------- tiles de fundo: 0 ceu, 1 parede, 2 janela acesa, 3 asfalto, 4 calcada, 5 sacada/cornija, 6 janela escura
BG_PAL = pal([(14, 16, 40), (44, 40, 70), (255, 214, 100), (30, 30, 38), (120, 120, 134), (170, 170, 184), (130, 90, 60), (24, 24, 44)])
def solid(n): return [n * 0x11111111] * 8
def rows(fn):
    out = []
    for y in range(8):
        v = 0
        for x in range(8):
            v |= fn(x, y) << (4 * x)
        out.append(v)
    return out
BG_TILES = (
    solid(0) +
    rows(lambda x, y: 1) +
    rows(lambda x, y: 2 if 1 <= x <= 6 and 1 <= y <= 6 else 1) +
    rows(lambda x, y: 3 if (y != 4 or x % 4 != 0) else 4) +
    rows(lambda x, y: 5 if y == 0 else 4) +
    rows(lambda x, y: 6 if y < 3 else 7) +
    rows(lambda x, y: 7 if 1 <= x <= 6 and 1 <= y <= 6 else 1)
)

# ---------- fase
WORLD = 512
GROUND = 128
CARS = [(64, 0), (176, 1), (288, 0), (392, 1)]               # (x, paleta 0 vermelho / 1 azul)
LEDGES = [(150, 88, 48), (262, 88, 40), (370, 72, 32)]        # (x, y, largura) - passa por baixo, pisa por cima
DOGS = [(104, 152), (216, 264), (328, 376), (432, 464)]       # (x minimo, x maximo)

random.seed(7)
cols, rows_n = 64, 32
bg = [[0] * cols for _ in range(rows_n)]
c = 0
while c < cols:
    wd = random.randint(5, 9)
    top = random.randint(3, 10)
    for cc in range(c, min(c + wd, cols)):
        for r in range(top, 16):
            lit = ((cc * 7 + r * 3) % 5) < 2
            bg[r][cc] = (2 if lit else 6) if (r % 3 == 1 and (cc - c) % 2 == 1) else 1
    c += wd + random.randint(0, 1)
for cc in range(cols):
    bg[16][cc] = 4
    for r in range(17, rows_n):
        bg[r][cc] = 3
for (lx, ly, lw) in LEDGES:
    for cc in range(lx // 8, (lx + lw) // 8):
        bg[ly // 8][cc] = 5
# mapa 64x32 = dois screenblocks 32x32 sequenciais
sb = []
for half in range(2):
    for r in range(32):
        for cc in range(32):
            sb.append(bg[r][half * 32 + cc])

# ---------- sprites: ordem dos tiles na VRAM de objetos
TILE_CAT0, TILE_CAT1, TILE_DOG0, TILE_DOG1, TILE_CAR, TILE_HEART = 0, 4, 8, 12, 16, 24
spr = (tiles_from_grid(CAT0, 16, 16) + tiles_from_grid(CAT1, 16, 16) +
       tiles_from_grid(DOG0, 16, 16) + tiles_from_grid(DOG1, 16, 16) +
       tiles_from_grid(CAR, 32, 16) + tiles_from_grid(HEART, 8, 8))

def carr(name, vals, t='u32', fmt='0x%08X'):
    s = 'static const %s %s[%d] = {\n' % (t, name, len(vals))
    for i in range(0, len(vals), 8):
        s += '  ' + ', '.join(fmt % v for v in vals[i:i + 8]) + ',\n'
    return s + '};\n'

with open('gfx.h', 'w') as f:
    f.write('/* GERADO por gen_gfx.py - nao edite a mao */\n#ifndef GFX_H\n#define GFX_H\n')
    f.write('typedef unsigned int u32; typedef unsigned short u16;\n')
    f.write('#define WORLD %d\n#define GROUND %d\n' % (WORLD, GROUND))
    f.write('#define TILE_CAT0 %d\n#define TILE_CAT1 %d\n#define TILE_DOG0 %d\n#define TILE_DOG1 %d\n#define TILE_CAR %d\n#define TILE_HEART %d\n'
            % (TILE_CAT0, TILE_CAT1, TILE_DOG0, TILE_DOG1, TILE_CAR, TILE_HEART))
    f.write(carr('spr_tiles', spr))
    f.write(carr('bg_tiles', BG_TILES))
    f.write(carr('bg_map', sb, 'u16', '%d'))
    f.write(carr('bg_pal', BG_PAL, 'u16', '0x%04X'))
    for i, p in enumerate(PAL_CAT):
        f.write(carr('pal_cat%d' % i, p, 'u16', '0x%04X'))
    f.write(carr('pal_dog', PAL_DOG, 'u16', '0x%04X'))
    f.write(carr('pal_car0', PAL_CAR_RED, 'u16', '0x%04X'))
    f.write(carr('pal_car1', PAL_CAR_BLUE, 'u16', '0x%04X'))
    f.write(carr('pal_heart', PAL_HEART, 'u16', '0x%04X'))
    f.write('#define NCARS %d\nstatic const short cars[NCARS][2] = {%s};\n' % (len(CARS), ','.join('{%d,%d}' % c for c in CARS)))
    f.write('#define NLEDGES %d\nstatic const short ledges[NLEDGES][3] = {%s};\n' % (len(LEDGES), ','.join('{%d,%d,%d}' % l for l in LEDGES)))
    f.write('#define NDOGS %d\nstatic const short dogs[NDOGS][2] = {%s};\n' % (len(DOGS), ','.join('{%d,%d}' % d for d in DOGS)))
    f.write('#endif\n')
print('gfx.h gerado')

# ---------- previa PNG dos sprites
try:
    from PIL import Image
    def rgb(p, i):
        v = p[i]; return ((v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3)
    S = 8
    img = Image.new('RGB', (16 * S * 5 + 60, 16 * S + 20), (14, 16, 40))
    def draw(grid, p, ox, oy=10):
        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                if ch != '.':
                    col = rgb(p, int(ch))
                    for dy in range(S):
                        for dx in range(S):
                            img.putpixel((ox + x * S + dx, oy + y * S + dy), col)
    draw(CAT0, PAL_CAT[0], 10); draw(CAT0, PAL_CAT[1], 150); draw(CAT0, PAL_CAT[2], 290)
    draw(DOG0, PAL_DOG, 430)
    img.save('previa_sprites.png')
    print('previa_sprites.png gerada')
except Exception as e:
    print('sem previa:', e)
