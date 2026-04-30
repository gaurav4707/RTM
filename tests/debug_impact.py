from service.trace_service import TraceService
import os

path = 'tmp_debug.db'
if os.path.exists(path):
    os.remove(path)

s = TraceService(db_path=path)

s.db.clear_all_data()

s.add_requirement('REQ-001', 'Root', 'Functional')
s.add_requirement('REQ-002', 'Inter', 'Functional')
s.add_requirement('REQ-003', 'Leaf', 'Functional')

s.link_requirement_dependency('REQ-001', 'REQ-002')
s.link_requirement_dependency('REQ-002', 'REQ-003')

s.add_design_module('DM-002', 'Intermediate', 'd')
s.add_design_module('DM-003', 'Leaf', 'd')

s.add_test_case('TC-003', 'Leaf test', 'exp')

print('link REQ-002->DM-002', s.link_requirement_to_design('REQ-002', 'DM-002'))
print('link REQ-003->DM-003', s.link_requirement_to_design('REQ-003', 'DM-003'))
print('link REQ-003->TC-003', s.link_requirement_to_test('REQ-003', 'TC-003'))

print('full impact REQ-002:', s.get_full_impact_analysis('REQ-002'))
