"""Content-bound review receipts. Run this code from a trusted base checkout."""
import hashlib,hmac,json,os,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
ROLES=('canon','knowledge','wiki')
def digest(root):
 h=hashlib.sha256()
 for p in sorted((root/'world').rglob('*')):
  if p.is_symlink():raise ValueError('symlinks forbidden in world')
  if p.is_file():h.update(str(p.relative_to(root)).encode()+b'\0'+p.read_bytes()+b'\0')
 return h.hexdigest()
def verdict(votes):
 if not isinstance(votes,list) or not all(isinstance(v,dict) for v in votes):return False
 if len(votes)!=3 or {v.get('role') for v in votes}!=set(ROLES):return False
 for v in votes:
  if v.get('verdict') not in ['approve','revise','reject'] or not isinstance(v.get('findings'),list):return False
  if not all(isinstance(f,dict) and f.get('severity') in ['blocker','warning'] and isinstance(f.get('ids'),list) and all(isinstance(f.get(k),str) and f[k] for k in ['reason','evidence','suggestion']) for f in v['findings']):return False
  if v['verdict']=='reject' or any(f.get('severity')=='blocker' for f in v['findings']):return False
 return sum(v['verdict']=='approve' for v in votes)>=2
def sign(receipt,key):
 data={k:v for k,v in receipt.items() if k!='signature'}
 return hmac.new(key.encode(),json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def verify(receipt,base,root,key):
 if not key:return False
 return receipt.get('base_commit')==base and receipt.get('world_digest')==digest(root) and verdict(receipt.get('votes',[])) and hmac.compare_digest(receipt.get('signature',''),sign(receipt,key))
def commit(root=ROOT):return subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
