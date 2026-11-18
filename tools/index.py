import json,pathlib,collections,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def generate(root=ROOT):
 records=[json.loads(p.read_text()) for p in sorted((root/'world/records').glob('*.json'))];groups=collections.defaultdict(list)
 for r in records:groups[r['kind']].append(r)
 files={}
 for kind,rs in groups.items():files[kind+'.md']='# '+kind+'\n\n'+'\n'.join(f'- [{r["name"]}](../wiki/{r["id"]}.md) — {r["summary"]}' for r in rs)+'\n'
 events={r['id']:r for r in records if r['kind']=='Event' and type(r.get('time')) is int}
 timeline=['# 확정 연표','', '연도 안의 목록 순서만으로 선후를 추측하지 않는다. 명시된 선후만 표시한다.','']
 for year in sorted({r['time'] for r in events.values()}):
  group={k:r for k,r in events.items() if r['time']==year};edges={k:set() for k in group};degree={k:0 for k in group}
  for rid,r in group.items():
   for field in ['after','before']:
    for ref in r.get(field,[]):
     if ref not in group:continue
     a,b=(ref,rid) if field=='after' else (rid,ref)
     if b not in edges[a]:edges[a].add(b);degree[b]+=1
  queue=sorted(k for k,d in degree.items() if not d);ordered=[]
  while queue:
   a=queue.pop(0);ordered.append(a)
   for b in sorted(edges[a]):
    degree[b]-=1
    if not degree[b]:queue.append(b);queue.sort()
  if len(ordered)!=len(group):raise ValueError('timeline cycle')
  timeline.append(f'## {year}년')
  timeline.append('')
  for rid in ordered:
   r=group[rid];timeline.append(f'- [{r["name"]}](../wiki/{rid}.md)')
  for a,targets in sorted(edges.items()):
   for b in sorted(targets):timeline.append(f'- 명시된 선후: {group[a]["name"]} → {group[b]["name"]}')
  timeline.append('')
 timeline.append('범위 사건과 미정 시점은 정확한 연도로 환산하지 않는다.')
 files['timeline.md']='\n'.join(timeline)+'\n'
 files['README.md']='# 분류 색인\n\n'+'\n'.join(f'- [{k} ({len(v)})]({k}.md)' for k,v in sorted(groups.items()))+'\n- [연표](timeline.md)\n'
 for name,text in files.items():
  path=root/'world/indexes'/name
  if '--check' in sys.argv:
   if not path.exists() or path.read_text()!=text:raise SystemExit('stale index: '+name)
  else:path.write_text(text)
if __name__=='__main__':generate()
