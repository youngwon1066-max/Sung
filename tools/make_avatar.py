"""피클 비서 기본 아바타(icons/pickle-avatar.png) 생성."""
from PIL import Image, ImageDraw
import os, math

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")
S = 1024
GREEN = (134, 210, 120)
GREEN_D = (94, 172, 92)
LILAC = (192, 132, 252)
DARK = (17, 22, 34)

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
# 배경 원 (라일락 계열 은은한 그라데이션 대신 단색 + 테두리)
d.ellipse([0, 0, S - 1, S - 1], fill=(38, 30, 56, 255))
d.ellipse([10, 10, S - 11, S - 11], fill=(46, 36, 70, 255))

# 피클 몸통 (둥근 캡슐형, 살짝 기울임)
body = Image.new("RGBA", (S, S), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
bd.rounded_rectangle([S*0.30, S*0.22, S*0.70, S*0.86], radius=int(S*0.20), fill=GREEN)
# 음영
bd.rounded_rectangle([S*0.52, S*0.22, S*0.70, S*0.86], radius=int(S*0.20), fill=GREEN_D)
body = body.rotate(-10, resample=Image.BICUBIC, center=(S/2, S/2))
img.alpha_composite(body)

# 꼭지
d = ImageDraw.Draw(img)
d.line([(S*0.53, S*0.24), (S*0.60, S*0.13)], fill=(104, 168, 96), width=int(S*0.035))
# 오이 돌기
for (cx, cy) in [(0.36,0.40),(0.33,0.55),(0.37,0.70),(0.45,0.33),(0.44,0.78)]:
    r = S*0.012
    d.ellipse([S*cx-r, S*cy-r, S*cx+r, S*cy+r], fill=(160, 226, 148))
# 눈
for ex in (0.40, 0.55):
    d.ellipse([S*ex, S*0.45, S*ex+S*0.075, S*0.54], fill=DARK)
    d.ellipse([S*ex+S*0.045, S*0.465, S*ex+S*0.062, S*0.487], fill=(255,255,255))
# 미소
d.arc([S*0.36, S*0.54, S*0.60, S*0.72], start=20, end=160, fill=DARK, width=int(S*0.022))
# 볼터치
d.ellipse([S*0.33, S*0.58, S*0.40, S*0.64], fill=(240, 130, 160))
d.ellipse([S*0.57, S*0.58, S*0.64, S*0.64], fill=(240, 130, 160))

# 둥근 마스크
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse([0, 0, S-1, S-1], fill=255)
img.putalpha(mask)
img.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, "pickle-avatar.png"))
print("saved pickle-avatar.png")
