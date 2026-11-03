import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from identity_policy import IdentityHypothesis

class ReadOnlyIdentityTests(unittest.TestCase):
 def test_readable_outside_pool_is_explorable_not_effect_qualified(self):
  candidate=IdentityHypothesis(True,352,False,False,None)
  self.assertTrue(candidate.may_read_bounded_projection());self.assertFalse(candidate.qualified_for_write_or_native_call())
 def test_unknown_pool_alignment_does_not_block_read(self):
  self.assertTrue(IdentityHypothesis(True,84,None,None,None).may_read_bounded_projection())
 def test_unreadable_or_unbounded_still_not_readable(self):
  for candidate in [IdentityHypothesis(False,84,False,False,None),IdentityHypothesis(True,65537,True,True,True),IdentityHypothesis(True,True,True,True,True)]:self.assertFalse(candidate.may_read_bounded_projection())
 def test_strict_action_identity_remains_distinct(self):
  candidate=IdentityHypothesis(True,352,True,True,True,False)
  self.assertTrue(candidate.may_read_bounded_projection());self.assertFalse(candidate.qualified_for_write_or_native_call())
  self.assertTrue(IdentityHypothesis(True,352,True,True,True,True).qualified_for_write_or_native_call())

if __name__=='__main__':unittest.main()
