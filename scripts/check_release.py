#!/usr/bin/env python3
"""앱 deploy_ios.sh 용 릴리즈 노트 검사기 — content/releases.json 에 build N 항목이 있으면 exit 0, 아니면 비0.

    python3 scripts/check_release.py --build 5 [--latest]

--latest: 이 build 가 releases.json 의 가장 큰 build 인지도 확인(새 빌드 뒤에 낡은 항목만 있는 경우를 막는다).
Python 표준 라이브러리만. 항목 규격은 웹킷 releases(ipe.release-note/1 병합본: id·version·build·status·date·notes{lang:[...]}).
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "content", "releases.json")


def main(argv=None):
    ap = argparse.ArgumentParser(description="releases.json 에 build N 항목이 있는지 검사")
    ap.add_argument("--build", required=True, help="앱 빌드 번호(pubspec 의 +N)")
    ap.add_argument("--latest", action="store_true", help="이 build 가 가장 최신 항목이어야 한다")
    a = ap.parse_args(argv)
    try:
        rels = json.load(open(PATH, encoding="utf-8"))["releases"]
    except (OSError, ValueError, KeyError) as e:
        print(f"check_release: content/releases.json 을 읽을 수 없습니다 ({e})", file=sys.stderr)
        return 2
    builds = {}
    for r in rels:
        try:
            builds[int(r["build"])] = r
        except (KeyError, ValueError):
            print(f"check_release: build 가 숫자가 아닌 항목이 있습니다: {r.get('id')}", file=sys.stderr)
            return 2
    try:
        n = int(a.build)
    except ValueError:
        print(f"check_release: --build 는 정수여야 합니다: {a.build}", file=sys.stderr)
        return 2
    e = builds.get(n)
    if not e:
        print(f"check_release: build {n} 항목이 없습니다 (있는 build: {sorted(builds)})", file=sys.stderr)
        return 1
    if not any(e.get("notes", {}).get(l) for l in e.get("notes", {})):
        print(f"check_release: build {n} 항목에 노트 문구가 없습니다", file=sys.stderr)
        return 1
    if a.latest and n != max(builds):
        print(f"check_release: build {n} 이 최신이 아닙니다 (최신 build {max(builds)})", file=sys.stderr)
        return 1
    print(f"check_release: OK build {n} ({e.get('id')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
