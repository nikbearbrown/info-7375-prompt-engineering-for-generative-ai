"""Offline book research: constructed examples, not live model outputs.

Usage: python3 worked_examples.py /absolute/course/root
Prints JSON; changes only disposable temporary fixtures. Never reads credentials.
"""
import importlib.util
import json
import math
import platform
from pathlib import Path
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
modules = {}
for path in sorted((root / 'lessons').glob('*/code/main.py')):
    key = int(path.parents[1].name[:2])
    spec = importlib.util.spec_from_file_location(f'chapter_{key}', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    modules[key] = module

def rejected(fn):
    try:
        fn()
    except (ValueError, PermissionError) as exc:
        return {'rejected': True, 'error': str(exc)}
    raise AssertionError('Expected rejection did not occur')

out = {'python': platform.python_version(), 'mode': 'offline constructed fixtures', 'chapters': {}}
c = out['chapters']
m = modules[1]
c['01'] = {str(t): {'p': m.probabilities([1, 2, 3], t), 'counts': m.sample([1, 2, 3], 1000, 7, t)} for t in [.5, 1, 2]}
for t in [.5, 1, 2]:
    direct = [math.exp(x/t) / sum(math.exp(y/t) for y in [1, 2, 3]) for x in [1, 2, 3]]
    assert all(math.isclose(a, b) for a, b in zip(direct, c['01'][str(t)]['p']))
m = modules[2]
cases = ['not json', '{"answer":"x","sources":["missing"]}', '{"answer":"The fixture says red","sources":["s1"]}']
c['02'] = {'fixture_source': {'s1': 'The color is blue.'}, 'responses': cases, 'accepted': [m.validate(x, {'s1'}) for x in cases], 'format_rate': m.pass_rate(cases, {'s1'})}
assert c['02']['accepted'] == [False, False, True]
m = modules[3]
c['03'] = {'required': ['read', 'write'], 'missing': {s: m.missing(s, ['read', 'write']) for s in m.SURFACES}, 'read_trace': m.classify(['reason', 'read'])}
m = modules[4]
c['04'] = {'wrong_finish': m.run([{'name': 'lookup', 'key': 'color'}, {'name': 'finish', 'answer': 'red'}], {'color': 'blue'}), 'exhaustion': m.run([{'name': 'lookup', 'key': 'color'}]*5, {'color': 'blue'}, 2)}
assert c['04']['wrong_finish']['status'] == 'finished'
m = modules[5]
with tempfile.TemporaryDirectory(prefix='info7375-boundary-') as directory:
    base = Path(directory) / 'allowed'; base.mkdir()
    (base / 'escape').symlink_to(Path(directory))
    c['05'] = {'read_name': m.authorize(base, 'notes.md', 'read').name, 'traversal': rejected(lambda: m.authorize(base, '../outside', 'read')), 'symlink': rejected(lambda: m.authorize(base, 'escape/outside', 'read')), 'unapproved_write': rejected(lambda: m.authorize(base, 'notes.md', 'write'))}
m = modules[6]
# Constructed implementation comparison: hardcoding fixes one input only.
old = lambda x: x - 1
bad_patch = lambda x: 3
good_patch = lambda x: x + 1
c['06'] = {'inputs': [2, 5], 'expected': [3, 6], 'old': [old(x) for x in [2, 5]], 'bad_patch': [bad_patch(x) for x in [2, 5]], 'good_patch': [good_patch(x) for x in [2, 5]], 'review_without_approval': m.review(['app.py'], ['app.py'], True, False), 'diff': m.diff('return x - 1\n', 'return x + 1\n')}
m = modules[7]
c['07'] = {'score': m.cosine(m.vector('office hours'), m.vector('office hours appointment')), 'independent': 2/math.sqrt(6), 'synonym_miss': m.retrieve('tuition refund', {'a': 'fee reimbursement'}), 'tie_order': m.retrieve('cat', {'b': 'cat', 'a': 'cat'})}
assert math.isclose(c['07']['score'], c['07']['independent'])
m = modules[8]; server = m.Server()
messages = [{'jsonrpc':'2.0','id':1,'method':'tools/list'}, {'jsonrpc':'2.0','id':2,'method':'initialize','params':{'protocolVersion':'unsupported-fixture','capabilities':{},'clientInfo':{'name':'test','version':'1'}}}, {'jsonrpc':'2.0','method':'notifications/initialized'}, {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'lookup','arguments':{'key':'missing'}}}]
c['08'] = [{'request': msg, 'response': server.handle(msg)} for msg in messages]
m = modules[9]; data = [(-2,0),(-1,0),(1,1),(2,1)]
one = m.train(data, steps=1); trained = m.train(data)
assert math.isclose(one['w'], .15) and one['b'] == 0
held = [(-3,0),(-.5,0),(.5,1),(3,1)]
predictions = [m.sigmoid(trained['w']*x+trained['b']) for x, _ in held]
c['09'] = {'train':data, 'one_step':one, 'trained':trained, 'held_out':held, 'probabilities':predictions, 'correct':sum((p>=.5)==bool(y) for p,(_,y) in zip(predictions,held)), 'held_out_n':len(held), 'limit':'Constructed sign-separable data, not evidence of real-world generalization'}
eps=1e-6
finite_diff=(m.loss(data, eps, 0)-m.loss(data, -eps, 0))/(2*eps)
c['09']['finite_difference_gradient_at_zero']=finite_diff
assert math.isclose(finite_diff, -.75, abs_tol=1e-8)
m=modules[10]
c['10']={'order':m.order([{'id':'verify','after':['build']},{'id':'build','after':['inspect']},{'id':'inspect'}]), 'cycle':rejected(lambda:m.order([{'id':'a','after':['b']},{'id':'b','after':['a']}])), 'meaningless_complete':m.missing_fields({k:'x' for k in m.FIELDS})}
m=modules[11]
blocks=[{'type':'tool_use','id':'good','name':'add','input':{'a':17,'b':25}}, {'type':'tool_use','id':'bad','name':'add','input':{'a':True,'b':25}}]
c['11']={'results':m.results(blocks), 'independent_integer_sum':sum([17,25]), 'duplicate':rejected(lambda:m.results([blocks[0],blocks[0]])), 'unverified_finish':m.loop(lambda _: {'stop_reason':'end_turn','content':[{'type':'text','text':'Wrong fixture answer: 99'}]}, {'messages':[]})}
assert c['11']['results'][0]['content']=='42'
m=modules[12]; memory=m.Memory(); memory.write('claim','blue','s1',0)
first=memory.read('claim'); memory.write('claim','red','unverified source label',first['version'])
c['12']={'first_read':first, 'fresh_false_value':memory.read('claim'), 'stale_write':rejected(lambda:memory.write('claim','blue','s1',first['version']))}
m=modules[13]; p=m.demo()['proposal']; d={'approved':True,'approver':'SIMULATED reviewer, not a person','fingerprint':m.fingerprint(p)}
c['13']={'fixture_decision':d,'original_matches':m.approved(p,d),'changed_matches':m.approved({**p,'target':'different.md'},d)}
assert c['13']['original_matches'] and not c['13']['changed_matches']
m=modules[14]; record={k:'x' for k in m.FIELDS}; record.update(data_classes=['public'],retention_days=1)
c['14']={'meaningless_complete':m.assess(record),'external_write':m.assess({**record,'external_write':True}),'missing':m.assess({})}
m=modules[15]
with tempfile.TemporaryDirectory(prefix='info7375-packet-') as directory:
    c['15']={'empty':m.validate_packet(directory)}
    for name in m.ARTIFACTS:
        Path(directory, name+'.md').write_text('x'*40, encoding='utf-8')
    c['15']['meaningless_complete']=m.validate_packet(directory)
    assert c['15']['meaningless_complete']['structurally_complete']
print(json.dumps(out, indent=2))
