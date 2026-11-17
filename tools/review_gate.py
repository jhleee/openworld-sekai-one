"""Use trusted default-branch code, not a proposed replacement, for this check."""
import argparse,json,pathlib,subprocess,sys
from governance import verify
import os
p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,required=True);p.add_argument('--base',required=True);a=p.parse_args();root=a.root.resolve()
changed=subprocess.check_output(['git','diff','--name-only',a.base,'HEAD'],cwd=root,text=True).splitlines()
# Infrastructure changes require maintainer review, not a world-generation receipt.
protected=[x for x in changed if not x.startswith(('world/','work/'))]
if protected:raise SystemExit('Maintainer review required for infrastructure changes: '+', '.join(protected))
receipt_path=root/'work/reviews/latest.json'
if not receipt_path.exists():raise SystemExit('Independent review receipt missing')
receipt=json.loads(receipt_path.read_text())
if not verify(receipt,a.base,root,os.environ.get('REVIEW_SIGNING_KEY','')):raise SystemExit('Missing key, invalid consensus, stale content/base or forged receipt')
print('PASS authenticated three-role consensus for exact world content and base')
