import unittest,tempfile,pathlib,json,shutil,sys,copy
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from validate import check,frontmatter
from governance import digest,sign,verify,verdict
from session import claim,release
from agent_loop import apply_files,ask
class Contract(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);shutil.copytree(ROOT/'world',self.root/'world')
 def tearDown(self):self.tmp.cleanup()
 def modify(self,rid,**data):
  p=self.root/'world/records'/f'{rid}.json';r=json.loads(p.read_text());r.update(data);p.write_text(json.dumps(r,ensure_ascii=False))
 def codes(self):return {e['code'] for e in check(self.root)['errors']}
 def test_seed(self):self.assertEqual(check(ROOT)['errors'],[])
 def test_bad_ref(self):self.modify('NPC-TOMA',references=['MISSING']);self.assertIn('REFERENCE',self.codes())
 def test_no_article(self):(self.root/'world/wiki/NPC-TOMA.md').unlink();self.assertIn('ARTICLE_MISSING',self.codes())
 def test_details_drift(self):self.modify('NPC-TOMA',details=[{'heading':'改','text':'changed'}]);self.assertIn('ARTICLE_SCHEMA',self.codes())
 def test_before_birth(self):self.modify('EVT-FLOOD',time=279,requires_alive=['NPC-TOMA']);self.assertIn('ALIVE_TIME',self.codes())
 def test_after_death(self):self.modify('NPC-TOMA',death_status='dead',died=306);self.modify('EVT-FLOOD',requires_alive=['NPC-TOMA']);self.assertIn('ALIVE_TIME',self.codes())
 def test_same_year_death(self):self.modify('NPC-TOMA',death_status='dead',died=307);self.modify('EVT-FLOOD',requires_alive=['NPC-TOMA']);self.assertIn('ALIVE_ORDER',self.codes())
 def test_unknown_death_not_inferred(self):self.modify('NPC-TOMA',death_status='unknown');self.modify('EVT-FLOOD',requires_alive=['NPC-TOMA']);self.assertNotIn('ALIVE_TIME',self.codes())
 def test_range_not_exact(self):self.modify('EVT-FLOOD',time_status='range',earliest=306,latest=308);self.assertIn('EVENT_TIME',self.codes())
 def test_cycle(self):self.modify('EVT-FRACTURE',after=['EVT-COMPACT']);self.assertIn('EVENT_CYCLE',self.codes())
 def test_reverse_time(self):self.modify('EVT-FLOOD',after=['EVT-PASS']);self.assertIn('EVENT_ORDER',self.codes())
 def test_double_seat(self):self.modify('POW-WITNESS',seat='threshold');self.assertIn('POWER_EXCLUSIVE',self.codes())
 def test_double_holder(self):self.modify('POW-WITNESS',holder='HERO-SERIN');self.assertIn('POWER_EXCLUSIVE',self.codes())
 def test_bad_item_custody(self):self.modify('ITM-LANTERN',keeper='LOC-ESTEL');self.assertIn('ITEM_RELATION',self.codes())
 def test_undecided_claim_allowed(self):self.assertNotIn('CLAIM_TRUTH',self.codes())
 def test_broken_link(self):
  p=self.root/'world/wiki/NPC-TOMA.md';p.write_text(p.read_text()+'\n[bad](missing.md)');self.assertIn('LINK',self.codes())
 def test_keyword_warning_not_error(self):
  p=self.root/'world/wiki/NPC-TOMA.md';p.write_text(p.read_text()+'\n무한 생성은 금지한다.');r=check(self.root);self.assertEqual(r['errors'],[]);self.assertTrue(r['warnings'])
 def test_metadata_types(self):
  p=self.root/'world/wiki/NPC-TOMA.md';p.write_text(p.read_text().replace('category: "Character"','category: {}'));self.assertIn('ARTICLE_SCHEMA',self.codes())
 def test_restricted_paths(self):
  with self.assertRaises(ValueError):apply_files(self.root,[{'path':'AGENTS.md','content':'bypass'}],['AGENTS.md'])
  self.assertFalse((self.root/'AGENTS.md').exists())
 def test_batch_atomic_validation(self):
  p=self.root/'world/wiki/NPC-TOMA.md';original=p.read_text()
  with self.assertRaises(ValueError):apply_files(self.root,[{'path':'world/wiki/NPC-TOMA.md','content':'changed'},{'path':'AGENTS.md','content':'bad'}],['world/wiki/NPC-TOMA.md'])
  self.assertEqual(p.read_text(),original)
 def test_symlink_escape(self):
  (self.root/'world/wiki/escape.md').symlink_to('/tmp/outside')
  with self.assertRaises(ValueError):apply_files(self.root,[{'path':'world/wiki/escape.md','content':'bad'}],['world/wiki/escape.md'])
 def votes(self):return [{'role':r,'verdict':'approve','findings':[]} for r in ['canon','knowledge','wiki']]
 def test_consensus(self):self.assertTrue(verdict(self.votes()))
 def test_missing_role(self):self.assertFalse(verdict(self.votes()[:2]))
 def test_duplicate_role(self):v=self.votes();v[2]['role']='canon';self.assertFalse(verdict(v))
 def test_approve_with_blocker(self):
  v=self.votes();v[0]['findings']=[{'severity':'blocker','ids':[],'reason':'cost','evidence':'rule','suggestion':'fix'}];self.assertFalse(verdict(v))
 def test_reviewer_error(self):v=self.votes();v[0]['verdict']='error';self.assertFalse(verdict(v))
 def test_receipt_tamper_and_stale(self):
  r={'base_commit':'base','world_digest':digest(self.root),'votes':self.votes()};r['signature']=sign(r,'secret');self.assertTrue(verify(r,'base',self.root,'secret'));self.assertFalse(verify(r,'next',self.root,'secret'));self.assertFalse(verify(r,'base',self.root,''));r['votes'][0]['verdict']='revise';self.assertFalse(verify(r,'base',self.root,'secret'))
 def test_content_change_invalidates(self):
  r={'base_commit':'base','world_digest':digest(self.root),'votes':self.votes()};r['signature']=sign(r,'secret');self.modify('NPC-TOMA',name='다른 이름');self.assertFalse(verify(r,'base',self.root,'secret'))
 def test_lease_exclusive_and_release(self):
  a=claim('T','one',root=self.root)
  with self.assertRaises(ValueError):claim('T','two',root=self.root)
  with self.assertRaises(ValueError):release('T','wrong',root=self.root)
  release('T',a['token'],root=self.root);self.assertEqual(claim('T','two',root=self.root)['owner'],'two')
 def test_lease_expiration(self):
  with patch('session.time.time',return_value=0):claim('T','one',1,self.root)
  self.assertEqual(claim('T','two',root=self.root)['owner'],'two')
 def test_lookup_is_bounded_and_readonly(self):
  data={'A':{'id':'A','name':'test'}};original=copy.deepcopy(data)
  with patch('agent_loop.completion',side_effect=[{'action':'lookup','ids':['A']},{'verdict':'approve'}]) as c:
   self.assertEqual(ask([],data),{'verdict':'approve'});self.assertEqual(c.call_count,2)
  self.assertEqual(data,original)
 def test_lookup_limit(self):
  with patch('agent_loop.completion',return_value={'action':'lookup','ids':['A']}):
   with self.assertRaises(ValueError):ask([],{'A':{}})
if __name__=='__main__':unittest.main()
