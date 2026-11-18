"""Build a single, offline HTML wiki from committed content. No network or dependencies."""
import argparse,json,pathlib
from validate import frontmatter,check
ROOT=pathlib.Path(__file__).resolve().parents[1]
def build(root=ROOT):
 report=check(root)
 if report['errors']:raise ValueError('Fix static validation errors before building viewer')
 pages=[]
 for path in sorted((root/'world/wiki').glob('*.md')):
  meta,body=frontmatter(path);record=json.loads((root/'world/records'/f'{meta["record"]}.json').read_text());pages.append(dict(meta,body=body,data=record))
 for slug,path in [('overview','world/overview.md'),('constitution','world/constitution.md'),('timeline','world/indexes/timeline.md')]:pages.append({'record':slug,'name':{'overview':'세계 개요','constitution':'세계 헌장','timeline':'연표'}[slug],'category':'Guide','tags':[],'references':[],'body':(root/path).read_text(),'data':None})
 payload=json.dumps({'pages':pages,'articles':report['articles']},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
 template=(root/'viewer/src/shell.html').read_text();css=(root/'viewer/src/style.css').read_text();js=(root/'viewer/src/app.js').read_text()
 html=template.replace('/*__STYLE__*/',css).replace('/*__APP__*/',js).replace('/*__DATA__*/',payload)
 return html
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();html=build();out=ROOT/'viewer/arken-wiki.html'
 if a.check:
  if not out.exists() or out.read_text()!=html:raise SystemExit('Viewer stale: run python tools/build_viewer.py')
  print('PASS viewer matches source')
 else:out.write_text(html);print(f'{out} ({len(html.encode()):,} bytes)')
