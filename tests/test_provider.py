import unittest,sys,pathlib,json,urllib.error
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'))
from agent_loop import completion
class Response:
 def __init__(self,choice):self.data=json.dumps({'choices':[choice]}).encode()
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self):return self.data
class ProviderTests(unittest.TestCase):
 def setUp(self):
  self.env=patch.dict('os.environ',{'LLM_ENDPOINT':'https://example.invalid/v1/chat/completions','LLM_API_KEY':'test-key','LLM_MODEL':'test'});self.env.start();self.addCleanup(self.env.stop)
 def test_auth_failure_no_retry(self):
  with patch('agent_loop.urllib.request.urlopen',side_effect=urllib.error.HTTPError('https://example.invalid',401,'no',{},None)) as request:
   with self.assertRaises(RuntimeError):completion([])
   self.assertEqual(request.call_count,1)
 def test_retry_transient(self):
  with patch('agent_loop.urllib.request.urlopen',side_effect=[TimeoutError(),Response({'finish_reason':'stop','message':{'content':'{"ok":true}'}})]) as request,patch('agent_loop.time.sleep'):
   self.assertEqual(completion([]),{'ok':True});self.assertEqual(request.call_count,2)
 def test_truncated_never_accepted(self):
  with patch('agent_loop.urllib.request.urlopen',return_value=Response({'finish_reason':'length','message':{'content':'{"ok":true}'}})) as request,patch('agent_loop.time.sleep'):
   with self.assertRaises(RuntimeError):completion([])
   self.assertEqual(request.call_count,4)
 def test_tool_calls_not_executed(self):
  with patch('agent_loop.urllib.request.urlopen',return_value=Response({'finish_reason':'tool_calls','message':{'content':'{"ok":true}'}})),patch('agent_loop.time.sleep'):
   with self.assertRaises(RuntimeError):completion([])
