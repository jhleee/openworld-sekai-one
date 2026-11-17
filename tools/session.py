"""Local cooperative lease and durable handoff. Separate machines need central scheduling."""
import argparse,fcntl,json,pathlib,time,uuid,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
def claim(task,owner,ttl=1800,root=ROOT):
 if ttl<1 or ttl>7200:raise ValueError('lease TTL must be 1..7200 seconds')
 runtime=root/'.runtime';runtime.mkdir(exist_ok=True)
 with (runtime/'leases.lock').open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);path=runtime/'leases.json';leases=json.loads(path.read_text()) if path.exists() else {};old=leases.get(task)
  if old and old['expires']>time.time():raise ValueError('task already leased; use renew with token')
  lease={'task':task,'owner':owner,'token':uuid.uuid4().hex,'expires':time.time()+ttl};leases[task]=lease
  tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(leases));os.replace(tmp,path);return lease
def release(task,token,root=ROOT):
 runtime=root/'.runtime';path=runtime/'leases.json'
 with (runtime/'leases.lock').open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);leases=json.loads(path.read_text())
  if leases.get(task,{}).get('token')!=token:raise ValueError('lease ownership changed')
  del leases[task];tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(leases));os.replace(tmp,path)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('task');p.add_argument('--owner',required=True);p.add_argument('--ttl',type=int,default=1800);a=p.parse_args();print(json.dumps(claim(a.task,a.owner,a.ttl)))
