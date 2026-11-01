"""A small, dependency-free, escaping-first Markdown renderer for the site build.

It covers the subset this repository writes: ATX headings, paragraphs, flat
ordered/unordered lists, fenced code, pipe tables with alignment, blockquotes,
horizontal rules, and inline code / bold / italic / links. Raw HTML is always
escaped, except a literal ``<br>`` (used inside generated table cells).

Link targets go through a caller-supplied ``resolve(href) -> href | None``;
returning ``None`` renders the link text without an anchor. Only http(s),
fragment and relative targets are ever emitted, so ``javascript:`` URLs cannot
survive even if ``resolve`` passes them through.
"""
import html
import re

__all__ = ["render", "slugify", "headings"]

_FENCE = re.compile(r"^(```|~~~)\s*([\w+-]*)\s*$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_ULIST = re.compile(r"^[-*+]\s+(.*)$")
_OLIST = re.compile(r"^(\d+)[.)]\s+(.*)$")
_HR = re.compile(r"^(?:-\s*){3,}$|^(?:\*\s*){3,}$|^(?:_\s*){3,}$")
_TABLE_SEP = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
_SAFE_SCHEME = re.compile(r"^(https?:|#|\.{0,2}/|[A-Za-z0-9_.-]+(/|$|#))")


def slugify(text):
    """GitHub-compatible heading anchor (lowercase, punctuation dropped, spaces to dashes)."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_\[\]]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def _split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, cur, in_code = [], [], False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def _find_link_end(text, start):
    """Index of the ')' closing a link target starting at text[start] (balanced parens)."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            if depth == 0:
                return i
            depth -= 1
        elif text[i] in " \n":
            return -1
    return -1


class _Inline:
    def __init__(self, resolve):
        self.resolve = resolve

    def __call__(self, text):
        out = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch == "\\" and i + 1 < n and text[i + 1] in "\\`*_[]()#+-.!|<>":
                out.append(html.escape(text[i + 1]))
                i += 2
            elif ch == "`":
                j = text.find("`", i + 1)
                if j == -1:
                    out.append("`")
                    i += 1
                else:
                    out.append("<code>" + html.escape(text[i + 1:j]) + "</code>")
                    i = j + 1
            elif text.startswith("<br>", i) or text.startswith("<br/>", i) or text.startswith("<br />", i):
                out.append("<br>")
                i = text.index(">", i) + 1
            elif ch == "[":
                rendered, i = self._link(text, i)
                out.append(rendered)
            elif text.startswith("**", i) or text.startswith("__", i):
                mark = text[i:i + 2]
                j = text.find(mark, i + 2)
                if j > i + 2:
                    out.append("<strong>" + self(text[i + 2:j]) + "</strong>")
                    i = j + 2
                else:
                    out.append(html.escape(mark))
                    i += 2
            elif ch in "*_":
                j = text.find(ch, i + 1)
                prev = text[i - 1] if i else " "
                opens = i + 1 < n and not text[i + 1].isspace()
                if ch == "_" and prev.isalnum():
                    opens = False
                if opens and j > i + 1 and not text[j - 1].isspace() and \
                        not (ch == "_" and j + 1 < n and text[j + 1].isalnum()):
                    out.append("<em>" + self(text[i + 1:j]) + "</em>")
                    i = j + 1
                else:
                    out.append(html.escape(ch))
                    i += 1
            else:
                j = i
                while j < n and text[j] not in "\\`<[*_":
                    j += 1
                if j == i:
                    out.append(html.escape(ch))
                    j = i + 1
                else:
                    out.append(html.escape(text[i:j]))
                i = j
        return "".join(out)

    def _link(self, text, i):
        depth, j = 0, i
        while j < len(text):
            if text[j] == "[":
                depth += 1
            elif text[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if j >= len(text) or j + 1 >= len(text) or text[j + 1] != "(":
            return html.escape("["), i + 1
        end = _find_link_end(text, j + 2)
        if end == -1:
            return html.escape("["), i + 1
        label = self(text[i + 1:j])
        target = text[j + 2:end].strip()
        href = self.resolve(target)
        if href is None or not _SAFE_SCHEME.match(href) or href.lower().startswith("javascript"):
            return label, end + 1
        attrs = ""
        if href.startswith(("http://", "https://")):
            attrs = ' rel="noopener noreferrer"'
        return '<a href="' + html.escape(href, quote=True) + '"' + attrs + ">" + label + "</a>", end + 1


def headings(source):
    """(level, text, slug) for every ATX heading outside fenced code."""
    found, in_fence = [], False
    for line in source.splitlines():
        if _FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        m = None if in_fence else _HEADING.match(line)
        if m:
            found.append((len(m.group(1)), m.group(2), slugify(m.group(2))))
    return found


def render(source, resolve=lambda href: href, heading_offset=0, drop_first_h1=False):
    """Render Markdown to HTML. Heading ids are unique within the document."""
    inline = _Inline(resolve)
    lines = source.replace("\r\n", "\n").split("\n")
    out, para, used = [], [], {}
    i = 0
    dropped = False

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(s.strip() for s in para)) + "</p>")
            para.clear()

    def unique(slug):
        base = slug or "section"
        k = used.get(base, 0)
        used[base] = k + 1
        return base if k == 0 else f"{base}-{k}"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        fence = _FENCE.match(stripped)
        if fence:
            flush()
            lang = fence.group(2)
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence.group(1)):
                body.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>" + html.escape("\n".join(body)) + "</code></pre>")
            continue
        if not stripped:
            flush()
            i += 1
            continue
        m = _HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            if level == 1 and drop_first_h1 and not dropped:
                dropped = True
                i += 1
                continue
            level = min(6, level + heading_offset)
            hid = unique(slugify(m.group(2)))
            out.append(f'<h{level} id="{html.escape(hid)}">{inline(m.group(2))}'
                       f'<a class="anchor" href="#{html.escape(hid)}" aria-label="Link to this section">#</a></h{level}>')
            i += 1
            continue
        if _HR.match(stripped):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1].strip()):
            flush()
            header = _split_row(stripped)
            aligns = []
            for cell in _split_row(lines[i + 1].strip()):
                cell = cell.strip()
                aligns.append("right" if cell.endswith(":") and not cell.startswith(":") else
                              "center" if cell.startswith(":") and cell.endswith(":") else "")
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(_split_row(lines[i].strip()))
                i += 1

            def cell(tag, text, k):
                a = aligns[k] if k < len(aligns) else ""
                style = f' class="al-{a}"' if a else ""
                return f"<{tag}{style}>{inline(text)}</{tag}>"
            parts = ['<div class="table-wrap"><table><thead><tr>']
            parts += [cell("th", h, k) for k, h in enumerate(header)]
            parts.append("</tr></thead><tbody>")
            for r in rows:
                r = (r + [""] * len(header))[:len(header)]
                parts.append("<tr>" + "".join(cell("td", c, k) for k, c in enumerate(r)) + "</tr>")
            parts.append("</tbody></table></div>")
            out.append("".join(parts))
            continue
        if stripped.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + render("\n".join(quote), resolve) + "</blockquote>")
            continue
        um, om = _ULIST.match(stripped), _OLIST.match(stripped)
        if (um or om) and not line.startswith("    "):
            flush()
            ordered = bool(om)
            pattern = _OLIST if ordered else _ULIST
            start = int(om.group(1)) if ordered else 1
            items = []
            while i < len(lines):
                cur = lines[i]
                mm = pattern.match(cur.strip())
                if mm and not cur.startswith("    "):
                    items.append([mm.group(2) if ordered else mm.group(1)])
                    i += 1
                elif items and cur.strip() and cur.startswith((" ", "\t")) and \
                        not _FENCE.match(cur.strip()):
                    items[-1].append(cur.strip())
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            attr = f' start="{start}"' if ordered and start != 1 else ""
            out.append(f"<{tag}{attr}>" + "".join(
                "<li>" + inline(" ".join(it)) + "</li>" for it in items) + f"</{tag}>")
            continue
        para.append(line)
        i += 1
    flush()
    return "\n".join(out) + "\n"
