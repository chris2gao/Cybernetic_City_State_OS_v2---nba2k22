"""Real temporary Git objects exercise discovery, provenance and same-candidate sync."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import project_context as context

class ProjectContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='project-context-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.git('init','-q');self.git('config','user.name','Synthetic Test');self.git('config','user.email','synthetic@example.invalid')
        self.index='product/INDEX.md';self.registry='product/MODULES.json';self.repository='test/project'
        self.catalog={'module_base':'product/','modules':[
            {'id':'parser','name':'Parser','status':'OFFLINE_ONLY','docs':['parser.md'],'artifacts':['parser.py']},
            {'id':'format','name':'Format','status':'STATIC_SOURCE','docs':['format.md'],'artifacts':['format.py']}]}
        for name,value in {'INDEX.md':'Parser and format entry','parser.md':'parser public instructions','format.md':'format instructions','parser.py':'print(1)','format.py':'print(2)'}.items():self.write('product/'+name,value)
        self.write(self.registry,json.dumps(self.catalog));self.base=self.commit('initial project')
    def git(self,*args):
        return subprocess.run(['git',*args],cwd=self.root,check=True,capture_output=True,text=True).stdout.strip()
    def write(self,path,value):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,encoding='utf-8')
    def commit(self,message):
        self.git('add','--','product');self.git('commit','-qm',message);return self.git('rev-parse','HEAD')
    def source(self,head):return context.GitSource(self.root,head,self.repository)
    def test_discovery_reads_only_selected_docs_and_frozen_bytes(self):
        self.write('product/parser.md','dirty changed instructions')
        doc=context.discover(self.source(self.base),self.index,self.registry,['parser'])
        self.assertEqual(doc['status'],'DISCOVERED_NOT_ACTIVATED')
        self.assertEqual(len(doc['modules']),2);self.assertEqual(len(doc['body_reads']),1)
        self.assertEqual(doc['body_reads'][0]['path'],'product/parser.md')
        self.assertFalse(doc['action_authorized'])
        self.assertEqual(doc['body_reads'][0]['blob'],self.git('rev-parse',self.base+':product/parser.md'))
    def test_no_catalog_does_not_create_domain_modules(self):
        self.assertEqual(context.discover(self.source(self.base),None,None)['status'],'PROJECT_CATALOG_NOT_DECLARED')
    def test_missing_or_escaping_selected_source_refused(self):
        self.catalog['modules'][0]['docs']=['missing.md'];self.write(self.registry,json.dumps(self.catalog));head=self.commit('missing doc')
        with self.assertRaises(context._source.PRMSError):context.discover(self.source(head),self.index,self.registry,['parser'])
        self.catalog['modules'][0]['docs']=['/outside'];self.write(self.registry,json.dumps(self.catalog));head=self.commit('absolute ref')
        with self.assertRaises((context._source.PRMSError,ValueError)):context.discover(self.source(head),self.index,self.registry)
    def test_actual_source_ancestry_overrides_claimed_master_status(self):
        self.write('product/parser.py','print(3)');candidate=self.commit('unpublished candidate')
        ref={'repository':self.repository,'commit':candidate,'path':'product/parser.py','publication_status':'SOURCE_BRANCH_NOT_MASTER'}
        self.assertEqual(context.source_status(self.source(candidate),ref,self.base)['actual_publication_status'],'SOURCE_BRANCH_NOT_MASTER')
        with self.assertRaisesRegex(ValueError,'publication_status'):context.source_status(self.source(candidate),dict(ref,publication_status='MASTER_INCLUDED'),self.base)
        with self.assertRaisesRegex(ValueError,'repository_mismatch'):context.source_status(self.source(candidate),dict(ref,repository='other/project'),self.base)
        with self.assertRaisesRegex(ValueError,'exact_source'):context.source_status(self.source(candidate),dict(ref,commit='HEAD'),self.base)
    def test_code_change_without_same_candidate_index_sync_pending(self):
        self.write('product/parser.py','print(3)');head=self.commit('code only')
        result=context.inspect_sync(self.source(self.base),self.source(head),self.index,self.registry,['parser'])
        self.assertEqual(result['status'],'INDEX_SYNC_PENDING');self.assertEqual(result['pending_module_ids'],['parser'])
    def test_unrelated_registry_row_cannot_mask_missing_affected_update(self):
        self.write('product/parser.py','print(3)');self.write(self.index,'new entry')
        self.catalog['modules'][1]['status']='UPDATED';self.write(self.registry,json.dumps(self.catalog));head=self.commit('wrong row')
        self.assertEqual(context.inspect_sync(self.source(self.base),self.source(head),self.index,self.registry,['parser'])['status'],'INDEX_SYNC_PENDING')
    def test_same_candidate_updates_correct_row_and_entry(self):
        self.write('product/parser.py','print(3)');self.write(self.index,'Parser updated, bounded offline evidence')
        self.catalog['modules'][0]['status']='OFFLINE_VERIFIED';self.write(self.registry,json.dumps(self.catalog));head=self.commit('complete sync')
        result=context.inspect_sync(self.source(self.base),self.source(head),self.index,self.registry,['parser'])
        self.assertEqual(result['status'],'INDEX_SYNCED_FOR_CANDIDATE')
        self.assertEqual(context.inspect_sync(self.source(self.base),self.source(head),self.index,self.registry,[])['status'],'INDEX_SYNC_PENDING')
    def handoff(self):
        return {'source_head':self.base,'result':'Parser API documented','remaining_gaps':[],
                'next_steps':['Independent review'],'plan_actual_deltas':[],
                'reproduction':['python -m unittest'],'evidence_scope':'Offline example, no target runtime'}
    def test_handoff_exact_head_gaps_and_workspace_ownership(self):
        record=self.handoff();self.assertEqual(context.validate_handoff(record,self.base),[])
        self.assertIn('handoff_exact_source_head',context.validate_handoff(dict(record,source_head='f'*40),self.base))
        record['shared_workspace']=True
        self.assertIn('handoff_shared_workspace_owner',context.validate_handoff(record,self.base))
        record.update(write_owner='execution A',next_owner='research B')
        self.assertEqual(context.validate_handoff(record,self.base),[])
        record.pop('remaining_gaps');self.assertTrue(context.validate_handoff(record,self.base))
    def test_final_review_requires_distinct_session_without_private_context(self):
        record=self.handoff();record.update(final_independent_review=True,reviewer_session='same',executor_session='same',private_executor_context_received=False)
        self.assertIn('handoff_review_isolation',context.validate_handoff(record,self.base))
        record.update(reviewer_session='fresh');self.assertEqual(context.validate_handoff(record,self.base),[])
        record['private_executor_context_received']=True
        self.assertIn('handoff_review_isolation',context.validate_handoff(record,self.base))
    def test_failure_budget_and_unknown_outcome(self):
        rows=[{'signature':'backend-timeout','remedy':str(i),'new_evidence':'trace '+str(i)} for i in range(3)]
        self.assertEqual(context.retry_disposition('backend-timeout',rows[:2]),'REPAIR_ALLOWED')
        self.assertEqual(context.retry_disposition('backend-timeout',rows),'JOINT_RESEARCH_REQUIRED')
        self.assertEqual(context.retry_disposition('backend-timeout',[rows[0],rows[0]]),'REPEATED_REMEDY_WITHOUT_EVIDENCE')
        self.assertEqual(context.retry_disposition('backend-timeout',[],external_outcome_unknown=True),'UNKNOWN_OUTCOME_NO_REPLAY')
if __name__=='__main__':unittest.main()
