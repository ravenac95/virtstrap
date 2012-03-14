"""
Test requirements locker
------------------------

"""
import os
import sys
import textwrap
import fudge
from fudge.inspector import arg
from nose.plugins.attrib import attr
from virtstrap.requirements import RequirementSet
from virtstrap.testing import *
from virtstrap.locker import *
from tests import fixture_path

def test_initialize_locker():
    locker = RequirementsLocker()

PACKAGES_DIR = fixture_path('packages')

class TestRequirementsLocker(object):
    def setup(self):
        self.pip_index_ctx = ContextUser(temp_pip_index(PACKAGES_DIR))
        self.index_url = self.pip_index_ctx.enter()
        self.temp_venv_ctx = ContextUser(temp_virtualenv())
        self.temp_dir = self.temp_venv_ctx.enter()
        # Install all of the packages
        pip_bin = os.path.join(self.temp_dir, 'bin/pip')
        python_version = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        site_packages = os.path.join(self.temp_dir, 
                'lib/python%s/site-packages/' % python_version)
        self.old_sys_path = sys.path
        sys.path.append(site_packages)
        output, return_code = call_and_capture([pip_bin, 'install', 'test1', 
            'test2', 'test3', 'test4', 'test5'])

    def teardown(self):
        sys.path = self.old_sys_path
        self.temp_venv_ctx.exit()
        self.pip_index_ctx.exit()
    
    @attr('slow')
    def test_locker_lock_requirements_set(self):
        requirements_list = ['test1', 'test5']
        req_set = RequirementSet.from_config_data(
                requirements_list)
        locker = RequirementsLocker()
        locked_req_str = locker.lock(req_set)
        expected_names = ['test1', 'test2', 'test3', 'test5']
        for expected in expected_names:
            assert expected in locked_req_str

        req_set = RequirementSet.from_config_data(
                requirements_list)

def test_initialize_dependency_graph():
    graph = RequirementsDependencyGraph()

#def test_initialize_dependency_graph_from_string():
#    data = textwrap.dedent("""
#    something1==0.10.5
#      something2==1.0
#      something3==1.2
#    something4==1.5.0
#      something5==0.5.0
#        something6==0.6.0
#    """))

class FakeGraphMixin(object):
    def setup_graph(self):
        fake_req1 = fudge.Fake()
        fake_req1.has_attr(name='fake1', req='fake1')
        fake_req2 = fudge.Fake()
        fake_req2.has_attr(name='fake2', req='fake2')
        fake_req3 = fudge.Fake()
        fake_req3.has_attr(name='fake3', req='fake3')
        fake_req4 = fudge.Fake()
        fake_req4.has_attr(name='fake4', req='fake4')
        fake_req5 = fudge.Fake()
        fake_req5.has_attr(name='fake5', req='fake5')

        graph = RequirementsDependencyGraph()

        graph.add_requirement(fake_req1)
        graph.add_requirement(fake_req5)
        graph.add_dependency(fake_req1, fake_req2)
        graph.add_dependency(fake_req2, fake_req3)
        graph.add_dependency(fake_req1, fake_req4)
        graph.add_dependency(fake_req5, fake_req2)
        graph.add_dependency(fake_req5, fake_req3)

        self.graph = graph

class TestRequirementsDependencyGraphBasic(object):
    """Basic tests on an empty graph"""
    def setup(self):
        graph = RequirementsDependencyGraph()
        self.graph = graph

    def test_add_requirement(self):
        fake_req = fudge.Fake()
        fake_req.has_attr(name='fake')
        graph = self.graph
        graph.add_requirement(fake_req)
        deps = graph.get_dependencies(fake_req)
        assert deps == []
        
    def test_add_distribution(self):
        fake_req1 = fudge.Fake()
        fake_req1.has_attr(name='fake1')
        fake_req2 = fudge.Fake()
        fake_req2.has_attr(name='fake2')
        graph = self.graph
        graph.add_requirement(fake_req1)
        graph.add_dependency('fake1', fake_req2)
        fake1_reqs = graph.get_dependencies('fake1')
        fake2_reqs = graph.get_dependencies('fake2')
        fake1_reqs_ignored = graph.get_dependencies('fake1', ignore=[fake_req2])
        assert fake1_reqs == [fake_req2]
        assert fake2_reqs == []
        assert fake1_reqs_ignored == []

class TestRequirementsDependencyGraphAdvanced(FakeGraphMixin):
    """Advanced tests using a graph with dependencies"""
    def setup(self):
        self.setup_graph()

    def test_get_all_dependencies(self):
        dependencies = self.graph.get_all_dependencies('fake1')
        dep_names = map(lambda a: a.name, dependencies)
        assert set(dep_names) == set(['fake2', 'fake4', 'fake3'])

def test_initialize_requirements_graph_display():
    graph = RequirementsDependencyGraph()
    display = RequirementsGraphDisplay(graph)

class TestRequirementsGraphDisplay(FakeGraphMixin):
    def setup(self):
        self.setup_graph()
        graph = self.graph
        self.display = RequirementsGraphDisplay(graph)

    def test_display_simple_reqs(self):
        display = self.display
        dep_str = display.show_dependencies(['fake4'])
        expected = 'fake4 (fake4)\n'
        assert dep_str == expected
    
    def test_display_single_dependency(self):
        display = self.display
        dep_str = display.show_dependencies(['fake2'])
        expected = 'fake2 (fake2)\n  fake3 (fake3)\n'
        assert dep_str == expected
    
    def test_display_multiple_dependencies(self):
        display = self.display
        dep_str = display.show_dependencies(['fake1', 'fake5'], 
                comment_doubles=True)
        expected = textwrap.dedent("""
            fake1 (fake1)
              fake2 (fake2)
                fake3 (fake3)
              fake4 (fake4)
            fake5 (fake5)
              fake2 (fake2)
                fake3 (fake3)
              fake3 (fake3)
        """)
        dep_str = dep_str.strip()
        expected = expected.strip()
        assert dep_str == expected

    def test_display_multiple_dependencies_case_insensitive(self):
        display = self.display
        dep_str = display.show_dependencies(['FAKE1', 'Fake5'],
                comment_doubles=True)
        expected = textwrap.dedent("""
            fake1 (fake1)
              fake2 (fake2)
                fake3 (fake3)
              fake4 (fake4)
            fake5 (fake5)
              fake2 (fake2)
                fake3 (fake3)
              fake3 (fake3)
        """)
        dep_str = dep_str.strip()
        expected = expected.strip()
        assert dep_str == expected

def test_initialize_joiner():
    joiner = RequirementsJoiner()

class TestRequirementsJoiner(FakeGraphMixin):
    def setup(self):
        self.setup_graph()
        JoinerShunt = shunt_class(RequirementsJoiner)
        self.joiner = JoinerShunt()

    def test_join_requirements(self):
        data = textwrap.dedent("""
            fake2
              fake3
        """)
        fake_display = fudge.Fake('fake_display')
        (self.joiner.__patch_method__('get_locked_display')
                .returns((fake_display, [])))
        fake_display.expects('show_dependencies').returns('fake2\n  fake3\n')
        requirements_list = ['fake1', 'fake5']
        req_set = RequirementSet.from_config_data(
                requirements_list)
        joined_str = self.joiner.join_to_str(requirement_set=req_set, 
                locked_string=data)
        expected = textwrap.dedent("""
        fake2
          fake3
        fake1
        fake5
        """)
        joined_str = joined_str.strip()
        expected = expected.strip()
        assert joined_str == expected

    def test_join_requirements_with_duplicates(self):
        data = textwrap.dedent("""
            fake2 (fake2==2)
              fake3 (fake3==3)
            fake1 (fake1==1)
        """)
        requirements_list = ['fake2','fake1', 'fake5']
        req_set = RequirementSet.from_config_data(
                requirements_list)
        joined_str = self.joiner.join_to_str(requirement_set=req_set, 
                locked_string=data)
        expected = textwrap.dedent("""
        fake2==2
          fake3==3
        fake1==1
        fake5
        """)
        joined_str = joined_str.strip()
        expected = expected.strip()
        assert joined_str == expected

    def test_join_requirements_no_locked_string(self):
        data = ''
        requirements_list = ['fake2','fake1', 'fake5']
        req_set = RequirementSet.from_config_data(
                requirements_list)
        joined_str = self.joiner.join_to_str(requirement_set=req_set, 
                locked_string=data)
        expected = textwrap.dedent("""
        fake2
        fake1
        fake5
        """)
        joined_str = joined_str.strip()
        expected = expected.strip()
        assert joined_str == expected


def test_initialize_locked_parser():
    locked_parser = LockedRequirementsParser()

class TestLockedRequirementsParser(object):
    def setup(self):
        fake_graph = fudge.Fake()
        self.parser = LockedRequirementsParser(graph=fake_graph)
        self.fake_graph = fake_graph

    @fudge.test
    def test_create_graph(self):
        fake_graph = self.fake_graph
        fake1_arg = arg.has_attr(name='fake1')
        fake2_arg = arg.has_attr(name='fake2')
        fake_graph.expects('add_requirement').with_args(fake1_arg)
        fake_graph.expects('add_dependency').with_args(fake1_arg, fake2_arg)
        self.parser.create_graph_from_string('fake1 (fake1)\n  fake2 (fake2)\n')
