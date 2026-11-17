"""Deterministic repository checks. Python 3.11+, no external packages."""
import argparse,json,re,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
KINDS={'Rule','Place','Event','Organization','Character','Power','Spirit','SacredBeast','Monster','Item','Claim','Thread','Fact','Belief','Culture'}
def frontmatter(path):
 text=path.read_text(encoding='utf-8');m=re.match(r'^---\n(.*?)\n---\n(.*)$',text,re.S)
 if not m:raise ValueError('missing JSON-value frontmatter')
 meta={}
 for line in m[1].splitlines():
  key,value=line.split(':',1)
  if key in meta:raise ValueError('duplicate metadata key')
  meta[key]=json.loads(value)
 return meta,m[2]
def check(root=ROOT):
 errors=[];warnings=[];records={};articles={}
 for p in root.rglob('*'):
  if '.git' not in p.parts and '.runtime' not in p.parts and p.is_symlink():return {'records':0,'articles':0,'errors':[{'code':'SYMLINK','path':str(p.relative_to(root)),'reason':'symlinks forbidden'}],'warnings':[]}
 def err(code,path,reason):errors.append({'code':code,'path':str(path.relative_to(root)),'reason':reason})
 for path in sorted((root/'world/records').glob('*.json')):
  try:
   r=json.loads(path.read_text());rid=r['id']
   if not isinstance(rid,str) or rid!=path.stem or rid in records:raise ValueError('ID must be unique and equal filename')
   if r.get('kind') not in KINDS:raise ValueError('unknown kind')
   if r.get('schema_version')!=1:raise ValueError('unsupported schema')
   for key in ['name','summary']:
    if not isinstance(r.get(key),str) or not r[key].strip():raise ValueError('missing '+key)
   if not isinstance(r.get('references'),list) or not all(isinstance(x,str) for x in r['references']):raise ValueError('references must be string array')
   if not isinstance(r.get('details'),list) or not all(isinstance(d,dict) and isinstance(d.get('heading'),str) and isinstance(d.get('text'),str) for d in r['details']):raise ValueError('invalid details')
   records[rid]=r
  except (ValueError,KeyError,TypeError) as e:err('RECORD_SCHEMA',path,str(e))
 for rid,r in records.items():
  path=root/'world/records'/f'{rid}.json'
  for ref in r['references']:
   if ref not in records:err('REFERENCE',path,ref)
  if r['kind']=='Claim' and r.get('truth') not in ['true','false','undecided']:err('CLAIM_TRUTH',path,'explicit truth required')
  if r['kind']=='Belief' and (r.get('holder') not in records or r.get('claim') not in records or records[r.get('claim')]['kind']!='Claim'):err('BELIEF',path,'holder and Claim required')
  if r['kind']=='Character':
   if type(r.get('born')) is not int or r.get('death_status') not in ['alive','dead','unknown']:err('LIFE',path,'explicit birth and status required')
   if r.get('death_status')=='dead' and (type(r.get('died')) is not int or r['died']<r.get('born',0)):err('LIFE',path,'confirmed death must follow birth')
  if r['kind']=='Item':
   if r.get('unique') is not True:err('UNIQUE',path,'initial Item schema represents unique items only')
   for key in ['owner','keeper']:
    if r.get(key) not in records or records.get(r.get(key),{}).get('kind') not in ['Character','Organization']:err('ITEM_RELATION',path,key)
  if r['kind']=='Fact':
   if type(r.get('start')) is not int or (r.get('end') is not None and (type(r['end']) is not int or r['end']<=r['start'])):err('FACT_TIME',path,'[start,end), explicit start, open end allowed')
   if r.get('certainty')!='confirmed' or r.get('temporal_kind')!='state':err('FACT_STATE',path,'only confirmed states; single action must be Event')
   for key in ['subject','target']:
    if r.get(key) not in records:err('FACT_REF',path,key)
  if r['kind']=='Event':
   if r.get('time_status')=='range':
    if r.get('time') is not None or type(r.get('earliest')) is not int or type(r.get('latest')) is not int or r['earliest']>r['latest']:err('EVENT_TIME',path,'invalid uncertain range')
   elif type(r.get('time')) is not int:err('EVENT_TIME',path,'exact integer or explicit range required')
   for target in r.get('requires_alive',[]):
    person=records.get(target,{})
    if person.get('kind')!='Character':err('ALIVE_REF',path,target);continue
    if type(r.get('time')) is int:
     if r['time']<person['born'] or (person.get('death_status')=='dead' and r['time']>person['died']):err('ALIVE_TIME',path,target)
     elif r['time']==person.get('died'):err('ALIVE_ORDER',path,'same-year death requires finer ordering')
  if r['kind']=='Power':
   if r.get('holder') not in records or records.get(r.get('holder'),{}).get('kind')!='Character':err('POWER_HOLDER',path,'Character required')
   if r.get('seat') not in ['threshold','witness','season','weight','sleep','return','name']:err('POWER_SEAT',path,'unknown seat')
   if type(r.get('start')) is not int or (r.get('end') is not None and (type(r['end']) is not int or r['end']<=r['start'])):err('POWER_TIME',path,'invalid tenure')
 # Iterative topological sort avoids recursion limits on long timelines.
 events={k:v for k,v in records.items() if v['kind']=='Event'};edges={k:set() for k in events};degree={k:0 for k in events}
 for rid,r in events.items():
  for field in ['after','before']:
   refs=r.get(field,[])
   if not isinstance(refs,list):err('EVENT_ORDER',root/'world/records'/f'{rid}.json','order must be array');continue
   for ref in refs:
    if ref not in events:err('EVENT_ORDER',root/'world/records'/f'{rid}.json','missing event '+str(ref));continue
    a,b=(ref,rid) if field=='after' else (rid,ref)
    if b not in edges[a]:edges[a].add(b);degree[b]+=1
    if type(events[a].get('time')) is int and type(events[b].get('time')) is int and events[a]['time']>=events[b]['time']:err('EVENT_ORDER',root/'world/records'/f'{rid}.json','strict before requires earlier time')
 queue=[k for k,d in degree.items() if d==0];visited=0
 while queue:
  a=queue.pop();visited+=1
  for b in edges[a]:
   degree[b]-=1
   if degree[b]==0:queue.append(b)
 if visited!=len(events):err('EVENT_CYCLE',root/'world/records','cyclic order')
 powers=[r for r in records.values() if r['kind']=='Power' and type(r.get('start')) is int]
 for i,a in enumerate(powers):
  for b in powers[i+1:]:
   if (a.get('seat')==b.get('seat') or a.get('holder')==b.get('holder')) and max(a['start'],b['start'])<min(a['end'] if a.get('end') is not None else float('inf'),b['end'] if b.get('end') is not None else float('inf')):err('POWER_EXCLUSIVE',root/'world/records'/f'{a["id"]}.json',b['id'])
 for path in sorted((root/'world/wiki').glob('*.md')):
  try:
   m,body=frontmatter(path);rid=m['record'];r=records.get(rid)
   if not r or rid in articles or path.stem!=rid or m.get('id')!='ART-'+rid:raise ValueError('one article per canonical record ID required')
   if m.get('category')!=r['kind'] or m.get('name')!=r['name']:raise ValueError('article name/category mismatch')
   tags=m.get('tags');refs=m.get('references')
   if not isinstance(tags,list) or not all(isinstance(t,str) and t.strip() for t in tags) or len(set(tags))<2:raise ValueError('at least two tags required')
   if not isinstance(refs,list) or rid not in refs or any(not isinstance(x,str) or x not in records for x in refs):raise ValueError('valid evidence IDs required')
   if len(re.sub(r'\s','',body))<240 or len(re.findall(r'^## ',body,re.M))<2:raise ValueError('article too short')
   # Seed articles expose structured details exactly; divergent editing must update both.
   if any(d['text'] not in body for d in r['details']):raise ValueError('record details and article drift')
   articles[rid]=m
   for word in ['최초','영원','무한','미확인']:
    if word in body:warnings.append({'code':'KEYWORD','path':str(path.relative_to(root)),'word':word})
  except (ValueError,KeyError,TypeError) as e:err('ARTICLE_SCHEMA',path,str(e))
 for rid in records:
  if rid not in articles:err('ARTICLE_MISSING',root/'world/records'/f'{rid}.json',rid)
 for path in root.rglob('*.md'):
  if '.git' in path.parts or '.runtime' in path.parts:continue
  for target in re.findall(r'\]\(([^)\s]+)\)',path.read_text()):
   if '://' in target or target.startswith('#'):continue
   dest=(path.parent/target.split('#')[0]).resolve()
   if not dest.is_relative_to(root.resolve()) or not dest.exists():err('LINK',path,target)
 return {'records':len(records),'articles':len(articles),'errors':errors,'warnings':warnings}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=ROOT);p.add_argument('--json',action='store_true');args=p.parse_args();r=check(args.root)
 print(json.dumps(r if args.json else {**{k:r[k] for k in ['records','articles']},'errors':r['errors'],'warning_count':len(r['warnings'])},ensure_ascii=False,indent=2));sys.exit(bool(r['errors']))
