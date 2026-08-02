#!/usr/bin/env python3
"""Join the extension docs into one printable HTML file.

Read-only. Takes the markdown as it is on disk and writes a single HTML file
somewhere else; nothing under the docs directory is modified.

Usage: md2html.py <docs-root> <output.html> <page.md> [page.md ...]

Deliberately small: it handles the subset of markdown these documents use
(headings, tables, fenced code, lists, blockquotes, links, inline emphasis and
code) rather than pulling in a dependency. If the docs start using something
more exotic, prefer pandoc over growing this.
"""
import base64
import html
import os
import re
import sys

CSS = """
@page { size: A4; margin: 20mm 18mm; }
body { font-family: "DejaVu Serif", Georgia, serif; font-size: 10.5pt;
       line-height: 1.45; color: #111; }
code, pre { font-family: "DejaVu Sans Mono", monospace; }
h1, h2, h3, h4, h5 { font-family: "DejaVu Sans", Helvetica, sans-serif;
       color: #000; line-height: 1.25; }
h1 { font-size: 20pt; margin: 0 0 .6em; page-break-before: always;
     border-bottom: 2px solid #333; padding-bottom: .2em; }
h1.first { page-break-before: avoid; }
h2 { font-size: 14pt; margin: 1.4em 0 .4em; }
h3 { font-size: 12pt; margin: 1.2em 0 .3em; }
h4, h5 { font-size: 10.5pt; margin: 1em 0 .3em; }
h1, h2, h3, h4, h5 { page-break-after: avoid; }
p { margin: .5em 0; orphans: 3; widows: 3; }
pre { background: #f4f4f4; border: 1px solid #ddd; border-radius: 3px;
      padding: .6em .8em; font-size: 8.5pt; line-height: 1.35;
      white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; }
code { background: #f4f4f4; padding: .1em .3em; border-radius: 2px; font-size: 9pt; }
pre code { background: none; padding: 0; font-size: inherit; }
table { border-collapse: collapse; width: 100%; margin: .8em 0; font-size: 9pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: .35em .5em; text-align: left;
         vertical-align: top; }
th { background: #eee; font-family: "DejaVu Sans", Helvetica, sans-serif; }
blockquote { border-left: 3px solid #ccc; margin: .8em 0; padding: .2em 0 .2em 1em;
             color: #444; }
ul, ol { margin: .5em 0; padding-left: 1.6em; }
li { margin: .25em 0; }
a { color: #05a; text-decoration: none; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }
figure { margin: 1em 0; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; height: auto; border: 1px solid #bbb; border-radius: 3px; }
figcaption { font-size: 8.5pt; color: #555; margin-top: .4em; text-align: left;
             line-height: 1.35; }
.cover { page-break-after: always; text-align: center; padding-top: 28vh; }
.cover h1 { font-size: 30pt; border: none; page-break-before: avoid; margin-bottom: .2em; }
.cover .sub { font-size: 13pt; color: #555; margin-bottom: 3em; }
.cover .note { font-size: 9.5pt; color: #666; max-width: 26em; margin: 0 auto;
               text-align: left; line-height: 1.5; }
.toc { page-break-after: always; }
.toc h1 { page-break-before: avoid; }
.toc ol { list-style: none; padding-left: 0; }
.toc ol ol { padding-left: 1.4em; }
.toc .part { font-family: "DejaVu Sans", Helvetica, sans-serif; font-weight: bold;
             margin-top: 1em; }
"""

IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
INLINE_CODE = re.compile(r'`([^`]+)`')
LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
BOLD = re.compile(r'\*\*([^*]+)\*\*')
ITALIC = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)')


IMG_ROOT = None   # set by main(); images resolve relative to the markdown file


def embed_image(src):
    """Read an image and return a data URI, or '' if it cannot be found.

    The HTML is built in a temp directory, so relative paths would not resolve.
    Inlining keeps the output a single self-contained file.
    """
    if src.startswith(('http:', 'https:', 'data:')):
        return src
    path = os.path.normpath(os.path.join(IMG_ROOT or '.', src))
    if not os.path.exists(path):
        print(f'  missing image: {src}', file=sys.stderr)
        return ''
    ext = os.path.splitext(path)[1].lstrip('.').lower()
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'gif': 'image/gif', 'svg': 'image/svg+xml'}.get(ext, 'image/png')
    with open(path, 'rb') as fh:
        return f'data:{mime};base64,' + base64.b64encode(fh.read()).decode()


def inline(text):
    """Escape, then apply inline markup. Code spans are protected first."""
    spans = []
    html_spans = []

    def stash_html(fragment):
        html_spans.append(fragment)
        return f'\x01{len(html_spans) - 1}\x01'

    def stash(m):
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    # Images first: they are ![alt](src) and would otherwise be eaten as links.
    def img(m):
        alt, src = m.group(1), m.group(2)
        data = embed_image(src)
        if not data:
            return ''
        return (f'<figure><img src="{data}" alt="{html.escape(alt, quote=True)}">'
                f'<figcaption>{html.escape(alt)}</figcaption></figure>')
    text = IMAGE.sub(lambda m: stash_html(img(m)), text)
    text = INLINE_CODE.sub(stash, text)
    text = html.escape(text)
    text = BOLD.sub(r'<strong>\1</strong>', text)
    text = ITALIC.sub(r'<em>\1</em>', text)
    # Links: internal .md targets become plain text, since there is no web
    # context in a PDF and a dead link is worse than none.
    def link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith('http'):
            return f'<a href="{html.escape(href, quote=True)}">{label}</a>'
        return label
    text = LINK.sub(link, text)
    for i, s in enumerate(spans):
        text = text.replace(f"\x00{i}\x00", f"<code>{html.escape(s)}</code>")
    for i, frag in enumerate(html_spans):
        text = text.replace(f"\x01{i}\x01", frag)
    return text


def gather_item(lines, i, first):
    """Join a list item's continuation lines onto its first line.

    A continuation is an indented, non-empty line that does not begin a new
    item or another block. Markdown treats those as part of the same item; not
    joining them renders each source line as its own bullet.
    """
    parts = [first]
    while i < len(lines):
        nxt = lines[i]
        if not nxt.strip():
            break
        if not re.match(r'^\s{2,}\S', nxt):
            break
        if re.match(r'^\s*([-*] |\d+\. |\||```|#{1,6} |> )', nxt):
            break
        parts.append(nxt.strip())
        i += 1
    return ' '.join(parts), i


def convert(md, slug):
    """Markdown to HTML for the subset these docs use."""
    out = []
    lines = md.split('\n')
    i = 0
    in_list = None
    first_heading = True

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f'</{in_list}>')
            in_list = None

    while i < len(lines):
        line = lines[i]

        fence = re.match(r'^(\s*)```', line)
        if fence:
            # An indented fence belongs to the list item above it, so keep the
            # list open and strip that indent from the body.
            pad = len(fence.group(1))
            if not pad:
                close_list()
            i += 1
            body = []
            while i < len(lines) and not re.match(r'^\s*```', lines[i]):
                body.append(lines[i][pad:] if lines[i][:pad].isspace() else lines[i])
                i += 1
            i += 1
            out.append('<pre><code>' + html.escape('\n'.join(body)) + '</code></pre>')
            continue

        m = re.match(r'^(#{1,6}) (.*)', line)
        if m:
            close_list()
            lvl = len(m.group(1))
            cls = ''
            if lvl == 1 and first_heading:
                cls = ' class="first"' if slug == 0 else ''
                first_heading = False
            anchor = re.sub(r'[^a-z0-9 -]', '', m.group(2).lower()).replace(' ', '-')
            out.append(f'<h{lvl} id="{slug}-{anchor}"{cls}>{inline(m.group(2))}</h{lvl}>')
            i += 1
            continue

        # table: a header row followed by a separator of dashes and pipes
        if (line.startswith('|') and i + 1 < len(lines)
                and re.match(r'^\|[\s:|-]+\|$', lines[i + 1])):
            close_list()
            def cells(row):
                return [c.strip() for c in row.strip().strip('|').split('|')]
            out.append('<table><thead><tr>')
            for c in cells(line):
                out.append(f'<th>{inline(c)}</th>')
            out.append('</tr></thead><tbody>')
            i += 2
            while i < len(lines) and lines[i].startswith('|'):
                out.append('<tr>')
                for c in cells(lines[i]):
                    out.append(f'<td>{inline(c)}</td>')
                out.append('</tr>')
                i += 1
            out.append('</tbody></table>')
            continue

        m = re.match(r'^(\s*)[-*] (.*)', line)
        if m:
            if in_list != 'ul':
                close_list()
                out.append('<ul>')
                in_list = 'ul'
            i += 1
            text, i = gather_item(lines, i, m.group(2))
            out.append(f'<li>{inline(text)}</li>')
            continue

        m = re.match(r'^(\s*)\d+\. (.*)', line)
        if m:
            if in_list != 'ol':
                close_list()
                out.append('<ol>')
                in_list = 'ol'
            i += 1
            text, i = gather_item(lines, i, m.group(2))
            out.append(f'<li>{inline(text)}</li>')
            continue

        if line.startswith('> '):
            close_list()
            out.append(f'<blockquote>{inline(line[2:])}</blockquote>')
            i += 1
            continue

        if not line.strip():
            close_list()
            i += 1
            continue

        # paragraph: gather until a blank line or a block starts
        close_list()
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r'^(#{1,6} |```|\||[-*] |\d+\. |> )', lines[i]):
            para.append(lines[i])
            i += 1
        out.append(f'<p>{inline(" ".join(para))}</p>')

    close_list()
    return '\n'.join(out)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    root, output, pages = sys.argv[1], sys.argv[2], sys.argv[3:]

    parts, toc, body = [], [], []
    for n, rel in enumerate(pages):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            print(f"skipping missing {rel}", file=sys.stderr)
            continue
        globals()['IMG_ROOT'] = os.path.dirname(path)
        md = open(path, encoding='utf-8').read()
        title = next((l[2:] for l in md.split('\n') if l.startswith('# ')), rel)
        # Group by directory. Top-level pages stand alone and are not given a
        # part heading, since they belong to no part by design.
        part = os.path.dirname(rel)
        if part and part not in parts:
            parts.append(part)
            toc.append(f'<li class="part">{html.escape(part.title())}</li>')
        anchor = re.sub(r'[^a-z0-9 -]', '', title.lower()).replace(' ', '-')
        toc.append(f'<li><a href="#{n}-{anchor}">{html.escape(title)}</a></li>')
        body.append(convert(md, n))

    doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Junk Store extensions</title>
<style>{CSS}</style></head><body>
<div class="cover">
  <h1>Junk Store</h1>
  <div class="sub">Extensions: user guide</div>
  <div class="note">
    This is a printable copy of the extension documentation. It was written by
    working through the source, and is a first pass at material that had not been
    documented before. It is accurate where it makes a claim, but it is not
    complete. Cross references between pages appear as plain text here; the
    online version links them.
  </div>
</div>
<div class="toc"><h1 class="first">Contents</h1><ol>{''.join(toc)}</ol></div>
{''.join(body)}
</body></html>"""
    with open(output, 'w', encoding='utf-8') as fh:
        fh.write(doc)
    print(f"wrote {output} ({len(pages)} pages)", file=sys.stderr)


if __name__ == '__main__':
    main()
