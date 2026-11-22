import json
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'concierge-cxas/cxas_app/DevFest_Concierge_atelier_simple'

class SimpleConciergeToolsTests(unittest.TestCase):
    def setUp(self):
        self.context=types.SimpleNamespace(state={})
        rows={r['session_id']:r for r in json.loads((ROOT/'data/agenda.json').read_text())}
        for row in rows.values():row.update(start=row['timeStart'],end=row['timeEnd'])
        self.calls=[]
        class Response:
            def __init__(self,row):self.row=row
            def raise_for_status(self):pass
            def json(self):return {'status':'ok','session':self.row} if self.row else {'status':'not_found'}
        def get_session(args):
            self.calls.append(args['session_id'])
            return Response(rows.get(args['session_id']))
        self.rows=rows
        self.env={'context':self.context,'tools':types.SimpleNamespace(sessions_api_get_session=get_session)}
        for p in (APP/'tools').glob('*/python_function/python_code.py'):exec(p.read_text(),self.env)
    def test_add_list_remove(self):
        f=self.env['update_personal_program'];sid='dfp26-48e0175b87dd'
        self.assertEqual(f('list'),{'status':'ok','sessions':[],'notice':'Sélection personnelle, aucune place réservée.'})
        self.assertEqual([r['session_id'] for r in f('add',sid)['sessions']],[sid])
        self.assertEqual([r['session_id'] for r in f('add',sid)['sessions']],[sid])
        self.assertEqual(self.calls,[sid])
        self.assertEqual([r['session_id'] for r in f('list')['sessions']],[sid])
        self.assertEqual(f('remove',sid)['sessions'],[])
    def test_conflict_preserves_selection(self):
        f=self.env['update_personal_program'];sid='dfp26-48e0175b87dd'
        f('add',sid)
        other=next(r for r in self.rows.values() if 'GitOps' in r['title'])
        res=f('add',other['session_id'])
        self.assertEqual(res['status'],'conflict')
        self.assertEqual([r['session_id'] for r in res['conflicts']],[sid])
        self.assertEqual(list(json.loads(self.context.state['personal_program'])),[sid])
    def test_unknown_session_is_not_added(self):
        f=self.env['update_personal_program']
        self.assertEqual(f('add','inconnue')['status'],'unavailable')
        self.assertNotIn('personal_program',self.context.state)
    def test_invalid_program_input(self):
        f=self.env['update_personal_program']
        self.assertEqual(f('reserve','x')['status'],'invalid_input')
        self.assertEqual(f('add')['status'],'invalid_input')
    def test_ticket_reuse_and_distinct_problem(self):
        f=self.env['create_support_ticket']
        one=f('technical','Le Wi-Fi ne fonctionne pas')
        two=f('technical','  le wi-fi  ne fonctionne pas  ')
        other=f('technical','Page blanche')
        self.assertEqual(one['status'],'ok')
        self.assertNotIn('simulated',one)
        self.assertTrue(one['ticket']['ticket_id'].startswith('TKT-'))
        self.assertEqual(one['ticket']['ticket_id'],two['ticket']['ticket_id'])
        self.assertNotEqual(one['ticket']['ticket_id'],other['ticket']['ticket_id'])
        self.assertEqual(len(json.loads(self.context.state['support_tickets'])),2)
    def test_invalid_ticket_input_does_not_write_state(self):
        f=self.env['create_support_ticket']
        for category,message in [('Facturation GCP','Problème'),('technical',''),('technical','x'*2001)]:
            self.assertEqual(f(category,message)['status'],'invalid_input')
        self.assertEqual(self.context.state,{})
    def test_invalid_ticket_state_reports_failure_without_reset(self):
        self.context.state['support_tickets']='not-json'
        self.assertEqual(self.env['create_support_ticket']('technical','Wi-Fi')['status'],'unavailable')
        self.assertEqual(self.context.state['support_tickets'],'not-json')

if __name__=='__main__':unittest.main()
