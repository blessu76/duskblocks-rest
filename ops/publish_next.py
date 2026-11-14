#!/usr/bin/env python3
"""큐(~/.ipe/queue/duskblocks/NN-slug/{en,ko}.md)의 가장 앞 글 하나를 발행한다.

content/journal/<slug>/ 로 복사하며 date·time 을 지금으로 찍고, build → scripts/check.sh → git commit.
push 는 기본 꺼짐(DUSK_PUSH=1 일 때만). 성공하면 큐 폴더를 .published/ 로 옮긴다.
종료 코드: 0 발행 · 3 큐 비었음(STOCK_ALERT) · 그 밖 실패.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import journal_md  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def next_folder(queue):
    names = sorted(n for n in os.listdir(queue)
                   if re.match(r"\d+-", n) and os.path.isdir(os.path.join(queue, n)))
    return names[0] if names else None


def stamp(text, date, hhmm):
    """front matter 의 date 를 바꾸고 time 을 넣는다."""
    head, sep, rest = text.partition("\n---\n")
    lines = [l for l in head.split("\n") if not l.startswith(("date:", "time:"))]
    out = []
    for l in lines:
        out.append(l)
        if l.startswith("title:"):
            out += [f"date: {date}", f'time: "{hhmm}"']
    return "\n".join(out) + sep + rest


def editions(folder):
    """발행할 언어판 [(lang, text)] — en·ko 원문은 필수, 나머지 10개 언어는 copy_review(iris)가 있는 것만(없으면 건너뛴다)."""
    out = []
    for lang in ("en", "ko"):
        with open(os.path.join(folder, lang + ".md"), encoding="utf-8") as f:
            out.append((lang, f.read()))
    for f in sorted(os.listdir(folder)):
        lang = f[:-3]
        if not f.endswith(".md") or lang in journal_md.ORIGINALS:
            continue
        with open(os.path.join(folder, f), encoding="utf-8") as fh:
            text = fh.read()
        meta, _ = journal_md.parse(text)
        if lang in languages_supported() and journal_md.is_reviewed(meta, lang):
            out.append((lang, text))
        else:
            print(f"SKIP {folder}/{f}: copy_review(iris) 없음 또는 지원 언어 아님 — 발행하지 않는다", file=sys.stderr)
    return out


def languages_supported():
    sys.path.insert(0, os.path.join(REPO, "vendor"))
    from ipe_web_kit import languages
    return languages.SUPPORTED


def sh(*cmd):
    return subprocess.run(cmd, cwd=REPO, check=True, text=True, capture_output=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--queue", required=True)
    a = ap.parse_args()
    name = next_folder(a.queue)
    if not name:
        print("STOCK_ALERT: duskblocks 저널 큐가 비었다", file=sys.stderr)
        return 3
    if sh("git", "rev-parse", "--abbrev-ref", "HEAD") != "main" or sh("git", "status", "--porcelain"):
        print("main 브랜치가 아니거나 작업 트리가 깨끗하지 않아 발행하지 않는다", file=sys.stderr)
        return 4
    slug = name.split("-", 1)[1]
    dst = os.path.join(REPO, "content", "journal", slug)
    os.makedirs(dst, exist_ok=True)
    for lang, text in editions(os.path.join(a.queue, name)):
        with open(os.path.join(dst, lang + ".md"), "w", encoding="utf-8") as f:
            f.write(stamp(text, a.date, a.time))
    try:
        sh("python3", "scripts/build.py")
        sh("bash", "scripts/check.sh")
        sh("git", "add", "-A")
        sh("git", "commit", "-m", f"저널: {slug} ({a.date} {a.time} KST)")
        if os.environ.get("DUSK_PUSH") == "1":
            sh("git", "push", "origin", "main")
    except subprocess.CalledProcessError as e:
        print((e.stdout or "") + (e.stderr or ""), file=sys.stderr)
        sh("git", "reset", "--hard", "HEAD")
        sh("git", "clean", "-fd", "--", "content/journal", "journal", "ko/journal")
        return 5
    done = os.path.join(a.queue, ".published")
    os.makedirs(done, exist_ok=True)
    shutil.move(os.path.join(a.queue, name), os.path.join(done, name))
    print(f"published {slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
