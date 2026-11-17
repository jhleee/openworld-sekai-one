import json,pathlib,collections,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def generate(root=ROOT):
 records=[json.loads(p.read_text()) for p in sorted((root/'world/records').glob('*.json'))];groups=collections.defaultdict(list)
 for r in records:groups[r['kind']].append(r)
 files={}
 for kind,rs in groups.items():files[kind+'.md']='# '+kind+'\n\n'+'\n'.join(f'- [{r["name"]}](../wiki/{r["id"]}.md) — {r["summary"]}' for r in rs)+'\n'
 files['timeline.md']='# 확정 연표\n\n'+'\n'.join(f'- {r["time"]}년: [{r["name"]}](../wiki/{r["id"]}.md)' for r in sorted([r for r in records if r['kind']=='Event' and type(r.get('time')) is int],key=lambda r:r['time']))+'\n\n범위 사건과 미정 시점은 정확한 연도로 환산하지 않는다.\n'
 files['README.md']='# 분류 색인\n\n'+'\n'.join(f'- [{k} ({len(v)})]({k}.md)' for k,v in sorted(groups.items()))+'\n- [연표](timeline.md)\n'
 for name,text in files.items():
  path=root/'world/indexes'/name
  if '--check' in sys.argv:
   if not path.exists() or path.read_text()!=text:raise SystemExit('stale index: '+name)
  else:path.write_text(text)
if __name__=='__main__':generate()
