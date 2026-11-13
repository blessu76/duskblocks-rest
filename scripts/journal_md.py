"""Tiny stdlib helpers for the journal: front matter + a small Markdown subset (paragraphs, ## / ### headings, - lists, 1. lists, **bold**, *italic*, `code`, [links](url))."""
import html
import os
import re


def parse(text):
    """Split `---` front matter (flat `key: value`, optional quotes) from the body. Returns (meta, body)."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for line in m.group(1).split("\n"):
        if not line.strip():
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[k.strip()] = v
    return meta, m.group(2).strip() + "\n"


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', s)
    return s


def render(body):
    out, para, lst = [], [], None

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        nonlocal lst
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    for line in body.split("\n"):
        s = line.rstrip()
        mh = re.match(r"(#{2,3})\s+(.*)", s)
        mu = re.match(r"-\s+(.*)", s)
        mo = re.match(r"\d+\.\s+(.*)", s)
        if not s:
            flush_para(); flush_list()
        elif mh:
            flush_para(); flush_list()
            n = len(mh.group(1))
            out.append(f"<h{n}>{inline(mh.group(2))}</h{n}>")
        elif mu or mo:
            flush_para()
            tag = "ul" if mu else "ol"
            if lst and lst[0] != tag:
                flush_list()
            lst = lst or (tag, [])
            lst[1].append((mu or mo).group(1))
        else:
            flush_list()
            para.append(s.strip())
    flush_para(); flush_list()
    return "\n".join(out)


def load_posts(root):
    """Return {slug: {lang: (meta, body)}} from content/journal/<slug>/<lang>.md."""
    base = os.path.join(root, "content", "journal")
    posts = {}
    if not os.path.isdir(base):
        return posts
    for slug in sorted(os.listdir(base)):
        d = os.path.join(base, slug)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".md"):
                meta, body = parse(open(os.path.join(d, f), encoding="utf-8").read())
                posts.setdefault(slug, {})[f[:-3]] = (meta, body)
    return posts
