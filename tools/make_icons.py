"""피클마린트래킹 PWA 아이콘 생성 스크립트 (Pillow).

실행: python3 tools/make_icons.py
결과: icons/icon-192.png, icon-512.png, icon-maskable-512.png, apple-touch-icon.png, favicon-32.png
"""
from PIL import Image, ImageDraw, ImageFilter
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")
S = 2048            # 슈퍼샘플링 캔버스
DESIGN = 1000       # 디자인 좌표계
BG1 = (11, 14, 20)          # #0b0e14
BG2 = (24, 33, 52)
CYAN = (6, 182, 212)
BLUE = (56, 189, 248)
WHITE = (241, 245, 249)
LILAC = (192, 132, 252)
DARK = (17, 22, 34)


def vgrad(size, c1, c2):
    strip = Image.new("RGB", (1, size))
    d = ImageDraw.Draw(strip)
    for y in range(size):
        t = y / (size - 1)
        d.point((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return strip.resize((size, size))


def draw_art(size):
    """투명 배경 위에 선박 + 항로를 그리고, 내용물 기준으로 잘라 반환."""
    scale = size / DESIGN
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = lambda v: v * scale
    P = lambda pts: [(u(x), u(y)) for x, y in pts]

    # 항로(뒤쪽 구간) + 앞쪽 구간
    route_back = [(60, 880), (150, 810), (250, 770), (350, 748)]
    route_front = [(660, 610), (770, 520), (830, 400), (860, 300)]
    for rp in (route_back, route_front):
        d.line(P(rp), fill=CYAN, width=max(2, int(u(24))), joint="curve")
    for (x, y) in [(60, 880), (350, 748), (860, 300)]:
        r = u(21)
        d.ellipse([u(x) - r, u(y) - r, u(x) + r, u(y) + r],
                  fill=(11, 14, 20), outline=BLUE, width=max(2, int(u(13))))

    # 선체 (우현 선수 방향)
    hull = [(300, 720), (360, 630), (700, 630), (790, 720), (740, 775), (350, 775)]
    d.polygon(P(hull), fill=WHITE)
    # 흘수선 포인트
    d.line(P([(345, 730), (755, 730)]), fill=CYAN, width=max(2, int(u(13))))
    # 화물창 4개
    for x in [368, 444, 520, 596]:
        d.rounded_rectangle([u(x), u(652), u(x + 62), u(714)], radius=u(9), fill=DARK)
    # 선교
    d.rounded_rectangle([u(660), u(548), u(736), u(630)], radius=u(11), fill=WHITE)
    for yy in (572, 598):
        d.rounded_rectangle([u(674), u(yy), u(722), u(yy + 10)], radius=u(5), fill=DARK)
    # 마스트 + 라일락 등화
    d.line(P([(698, 548), (698, 500)]), fill=WHITE, width=max(2, int(u(9))))
    d.ellipse([u(676), u(478), u(720), u(522)], fill=LILAC)
    # 선수 물보라
    d.line(P([(812, 748), (868, 748)]), fill=BLUE, width=max(2, int(u(13))))

    bbox = img.getbbox()
    return img.crop(bbox)


def make_icon(path, size, maskable=False, rounded=True, content=0.80):
    canvas = vgrad(S, BG2, BG1).convert("RGBA")
    # 은은한 중앙 글로우
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse([S * 0.08, S * 0.08, S * 0.92, S * 0.92], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.14))
    canvas = Image.composite(Image.new("RGBA", (S, S), (16, 42, 60, 255)), canvas, glow)

    art = draw_art(S)
    ratio = (0.68 if maskable else content)
    target = int(S * ratio)
    scale = target / max(art.width, art.height)
    art = art.resize((max(1, int(art.width * scale)), max(1, int(art.height * scale))), Image.LANCZOS)
    pos = ((S - art.width) // 2, (S - art.height) // 2)
    canvas.alpha_composite(art, pos)

    if rounded and not maskable:
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255)
        canvas.putalpha(mask)

    canvas.resize((size, size), Image.LANCZOS).save(path)
    print("saved", path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    make_icon(os.path.join(OUT, "icon-192.png"), 192)
    make_icon(os.path.join(OUT, "icon-512.png"), 512)
    make_icon(os.path.join(OUT, "icon-maskable-512.png"), 512, maskable=True, rounded=False, content=0.7)
    make_icon(os.path.join(OUT, "apple-touch-icon.png"), 180, maskable=True, rounded=False, content=0.7)
    make_icon(os.path.join(OUT, "favicon-32.png"), 32, content=0.88)
