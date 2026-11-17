"""Read-only recovery inspection. Never treats a handoff as proof of approval."""
import argparse,json,pathlib,subprocess,os
from governance import verify
from validate import check
p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,required=True);a=p.parse_args();root=a.root.resolve()
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();status=subprocess.check_output(['git','status','--short'],cwd=root,text=True)
receipt=root/'work/reviews/latest.json';valid=False
if receipt.exists():
 try:valid=verify(json.loads(receipt.read_text()),base,root,os.environ.get('REVIEW_SIGNING_KEY',''))
 except (ValueError,KeyError,TypeError):valid=False
report=check(root)
print(json.dumps({'head':base,'working_changes':status.splitlines(),'static_errors':report['errors'],'receipt_valid_against_HEAD':valid,'next_action':'If HEAD already includes the proposal, verify against its recorded base and current target branch before PR submission. Preserve interrupted drafts before starting a clean run. No merge or lease takeover performed.'},ensure_ascii=False,indent=2))
