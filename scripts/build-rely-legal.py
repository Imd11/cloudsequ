"""Rebuild public Rely pages from the selected version's Markdown. --check performs no writes."""
from html import escape
from pathlib import Path
import re, json, hashlib, argparse
ROOT = Path(__file__).resolve().parents[1]
LEGAL = ROOT / "legal/rely"
TITLE_LINKS = {}
def inline(text):
    text = escape(text.strip())
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    for title, target in TITLE_LINKS.items():
        text = text.replace(title, f'<a href="{target}">{title}</a>')
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text

def render_md(source):
    lines = source.splitlines()
    pieces, toc, paragraph = [], [], []
    list_type = None
    section = 0

    def flush():
        if paragraph:
            pieces.append("<p>" + "<br>".join(inline(x) for x in paragraph) + "</p>")
            paragraph.clear()

    def close_list():
        nonlocal list_type
        if list_type:
            pieces.append(f"</{list_type}>")
            list_type = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            flush()
            close_list()
            i += 1
            continue
        if line.startswith("|"):
            flush()
            close_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in row):
                    rows.append(row)
                i += 1
            pieces.append('<div class="table-wrap" role="region" aria-label="数据说明表" tabindex="0"><table>')
            for j, row in enumerate(rows):
                if j == 0:
                    pieces.append("<thead><tr>" + "".join(f'<th scope="col">{inline(c)}</th>' for c in row) + "</tr></thead><tbody>")
                else:
                    pieces.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            pieces.append("</tbody></table></div>")
            continue
        heading = re.match(r"^(#{1,3}) (.+)$", line)
        if heading:
            flush()
            close_list()
            level = len(heading[1])
            section += 1
            anchor = f"section-{section}"
            pieces.append(f'<h{level} id="{anchor}">{inline(heading[2])}</h{level}>')
            if level == 2:
                toc.append((anchor, heading[2]))
            i += 1
            continue
        if line.startswith("> "):
            flush()
            close_list()
            pieces.append(f'<aside class="draft-note">{inline(line[2:])}</aside>')
            i += 1
            continue
        item = re.match(r"^(?:([-]) |(\d+)\. )(.+)$", line)
        if item:
            flush()
            desired = "ul" if item[1] else "ol"
            if list_type != desired:
                close_list()
                start = f' start="{item[2]}"' if desired == "ol" and item[2] != "1" else ""
                pieces.append(f"<{desired}{start}>")
                list_type = desired
            pieces.append(f"<li>{inline(item[3])}</li>")
            i += 1
            continue
        close_list()
        paragraph.append(line)
        i += 1
    flush()
    close_list()
    return "\n".join(pieces), toc

def generated():
    catalog=json.loads((LEGAL / "manifest.json").read_text())
    version=catalog["version"]
    if not re.fullmatch(r"[a-zA-Z0-9.-]+",version):
        raise ValueError("Invalid version path")
    archive=LEGAL / "versions" / version
    assert catalog["status"] in ["draft","published"]
    assert len(catalog["documents"]) == 4
    pairs=[]
    result={}
    nav="".join('<a href="'+escape(d["url"])+ '">'+escape(d["title"])+ '</a>' for d in catalog["documents"])
    notice="草稿 · "+escape(version)+" · 尚未发布生效" if catalog["status"]=="draft" else "版本："+escape(version)+" · 生效日期："+escape(catalog["effectiveAt"])
    for doc in catalog["documents"]:
        ident=doc["id"]
        assert ident in ["terms","privacy","usage","providers"]
        assert doc["url"]=="https://cloudsequ.com/legal/rely/"+ident+"/"
        assert doc["archiveUrl"]=="https://cloudsequ.com/legal/rely/versions/"+version+"/"+ident+"/"
        raw=(archive/(ident+".md")).read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        assert digest==doc["sha256"], "Document changed: "+ident
        pairs.append([ident,digest])
        for archived in [False,True]:
            prefix="/legal/rely/versions/"+version+"/" if archived else "/legal/rely/"
            TITLE_LINKS.clear()
            TITLE_LINKS.update({"《Rely 用户协议》":prefix+"terms/", "《Rely 隐私政策》":prefix+"privacy/", "《Rely AI 内容使用规范》":prefix+"usage/", "《Rely 第三方服务与个人信息处理清单》":prefix+"providers/"})
            content,toc=render_md(raw.decode("utf-8"))
            sidebar='<nav class="toc" aria-label="本页目录"><span>本页目录</span>'+"".join('<a href="#'+a+'">'+escape(t)+'</a>' for a,t in toc)+'</nav>'
            page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer">'+('<meta name="robots" content="noindex,nofollow">' if catalog["status"]=="draft" else '')+'<title>Rely '+escape(doc["title"])+' · 云象序动</title><link rel="stylesheet" href="/legal/rely/legal.css"></head><body><a class="skip" href="#main">跳至正文</a><header class="site-header"><div class="header-inner"><a class="brand" href="/">云象序动<span>Rely</span></a><a href="mailto:support@cloudsequ.com">联系我们</a></div></header><div class="review-banner">'+notice+'</div><nav class="top-nav" aria-label="协议页面">'+nav+'</nav><div class="layout has-toc">'+sidebar+'<main id="main" tabindex="-1">'+content+'</main></div><footer><span>北京云象序动科技有限公司</span><a href="mailto:support@cloudsequ.com">support@cloudsequ.com</a><a href="'+escape(doc["archiveUrl"])+'">本版存档</a></footer></body></html>'
            result[(archive if archived else LEGAL)/ident/"index.html"]=page+"\n"
    digest=hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest()
    assert digest==catalog["bundleHash"], "Bundle changed"
    intro='<h1>Rely 协议与隐私政策</h1><p>'+notice+'</p>'
    intro+=''.join('<p><a href="'+d['id']+'/">'+escape(d['title'])+'</a></p>' for d in catalog['documents'])
    result[LEGAL/"index.html"]='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rely 协议与隐私政策 · 云象序动</title><link rel="stylesheet" href="/legal/rely/legal.css"></head><body><div class="layout"><main>'+intro+'</main></div></body></html>\n'
    if catalog["status"]=="published":
        assert catalog["effectiveAt"], "Published policies require a date"
        for p in archive.glob("*.md"):
            assert not any(x in p.read_text() for x in ["草稿", "正式发布时填写", "待填写"]), "Unreviewed text cannot be published"
    return result,catalog

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--app-catalog",type=Path)
    args=parser.parse_args()
    files,catalog=generated()
    if args.app_catalog:
        assert json.loads(args.app_catalog.read_text())==catalog,"App/website manifest mismatch"
    for path,html in files.items():
        if args.check:
            assert path.is_file() and path.read_text()==html,"Stale HTML: "+str(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(html)
    print("Rely: 4 source hashes, bundle and 9 pages verified" if args.check else "Rely: 9 pages generated")
if __name__=="__main__": main()
