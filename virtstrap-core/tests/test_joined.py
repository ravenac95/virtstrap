"""
Test joined requirements
------------------------

"""
import fudge
from virtstrap.joined import *

def fake_req(name, editable=False):
    fake = fudge.Fake()
    fake.has_attr(name=name, req=name, editable=editable)
    return fake

def test_joined_requirement_set():
    requirement_set = fudge.Fake('Requirement')
    locked_graph = fudge.Fake('LockedRequirementGraph')
    joined_requirement_set = JoinedRequirementSet.join(requirement_set, 
            locked_graph)

class RequirementSetFake(fudge.Fake):
    def __init__(self, *args, **kwargs):
        super(RequirementSetFake, self).__init__('RequirementSet', 
                *args, **kwargs)

    def __iter__(self):
        return iter(self.iter_func())

@fudge.test
def test_joined_requirement_set_iterate():
    fake1 = fake_req('fake1')
    fake2 = fake_req('fake2')
    fake3 = fake_req('fake3')
    fake4 = fake_req('fake4')
    fake5 = fake_req('fake5')

    requirement_set = RequirementSetFake()
    (requirement_set.expects('iter_func')
            .returns([fake1, fake2, fake5]))
    locked_graph = fudge.Fake('LockedRequirementSet')
    (locked_graph.expects('find').with_args('fake1').returns(fake1)
            .next_call().with_args('fake2').returns(fake2)
            .next_call().with_args('fake5').returns(fake5))

    (locked_graph.expects('get_all_dependencies').with_args('fake1').returns([fake2, fake3, fake4])
            .next_call().with_args('fake2').returns([fake3])
            .next_call().with_args('fake5').returns([fake1, fake2, fake3, fake4]))
    joined_requirement_set = JoinedRequirementSet.join(requirement_set, 
            locked_graph)

    expected = ['fake1', 'fake2', 'fake3', 'fake4', 'fake5']
    requirement_names = []
    for requirement in joined_requirement_set.as_list():
        requirement_names.append(requirement.name)

    requirement_names.sort()
    assert requirement_names == expected
