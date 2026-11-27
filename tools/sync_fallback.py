#!/usr/bin/env python3
"""data/fleet.json → index.html 내장 사본(#fleetFallbackData) 동기화 도구.

운항 추적(6시간 주기)으로 data/fleet.json 을 갱신한 뒤 한 번 돌려 주면
네트워크가 끊겼을 때 쓰는 내장 사본도 같은 내용이 됩니다.

사용 예:
    python3 tools/sync_fallback.py            # fleet.json 내용을 그대로 내장 사본에 반영
    python3 tools/sync_fallback.py --now      # updatedAt 을 현재 KST 시각으로 바꾼 뒤 반영
"""
import argparse
import datetime
import io
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
FLEET_PATH = ROOT / "data" / "fleet.json"
HTML_PATH = ROOT / "index.html"
KST = datetime.timezone(datetime.timedelta(hours=9))


def main() -> int:
    parser = argparse.ArgumentParser(description="fleet.json 을 index.html 내장 사본에 동기화")
    parser.add_argument("--now", action="store_true", help="updatedAt 을 현재 KST 시각으로 갱신")
    args = parser.parse_args()

    data = json.loads(FLEET_PATH.read_text(encoding="utf-8"))
    if args.now:
        data["updatedAt"] = datetime.datetime.now(KST).replace(microsecond=0).isoformat()
        FLEET_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pretty = json.dumps(data, ensure_ascii=False, indent=2)
    html = HTML_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<script type="application/json" id="fleetFallbackData">\n)(.*?)(\n  </script>)', re.S
    )
    new_html, count = pattern.subn(lambda m: m.group(1) + pretty + m.group(3), html)
    if count != 1:
        raise SystemExit(f"내장 사본 블록을 찾지 못했습니다 (매치 {count}건)")

    HTML_PATH.write_text(new_html, encoding="utf-8")
    print(f"동기화 완료: {len(data.get('fleet', []))}척 · updatedAt={data.get('updatedAt')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
