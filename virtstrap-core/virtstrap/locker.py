"""
virtstrap.locker
----------------

"""
from cStringIO import StringIO
import sys
import pip
import pkg_resources
from .requirements import RequirementSet

LEVEL_STR = '  '
COMMENT_PREFIX = '#::'

def get_distributions(requirements, sys_path=None, working_set=None):
    retriever = DistributionRetriever(sys_path=sys_path, 
            working_set=working_set)
    return retriever.get_distributions(requirements)

def get_distribution(name, sys_path=None, working_set=None):
    retriever = DistributionRetriever(sys_path=sys_path, 
            working_set=working_set)
    return retriever.get_distribution(name)

class DistributionRetriever(object):
    def __init__(self, sys_path=None, working_set=None):
        self._sys_path = sys_path or sys.path
        self._working_set = (working_set or 
                pkg_resources.WorkingSet(entries=sys_path))

    def get_distributions(self, reqs):
        names = map(lambda a: a.name, reqs)
        return self.get_distributions_with_names(names)

    def get_distributions_with_pkg_resource_requirements(self, reqs):
        names = map(lambda a: a.key, reqs)
        return self.get_distributions_with_names(names)

    def get_distributions_with_names(self, req_names):
        distributions = []
        for name in req_names:
            dist = self.get_distribution(name)
            distributions.append(dist)
        return distributions

    def get_distribution(self, name):
        working_set = self._working_set
        return working_set.by_key[name]

class RequirementsLocker(object):
    def lock(self, requirement_set):
        """Creates a locked requirement set"""
        # Build RequirementsDependencyGraph
        dep_graph = self.build_dependency_graph(requirement_set)
        display = RequirementsGraphDisplay(dep_graph)
        lock_string = display.show_dependencies(requirement_set)
        return lock_string

    def build_dependency_graph(self, requirement_set):
        """Build dependency graph"""
        # Initialize pip's version control modules
        # This is necessary to ensure we can determine if a project
        # is editable or not
        pip.version_control()
        # Create a frozen requirement for each installed dist
        dep_graph = RequirementsDependencyGraph()
        retriever = DistributionRetriever()
        dists = retriever.get_distributions(requirement_set)
        for dist in dists:
            self._collect_dependencies(dist, dep_graph, retriever)
        return dep_graph

    def _collect_dependencies(self, dist, graph, retriever, parent=None):
        req = pip.FrozenRequirement.from_dist(dist, [], find_tags=False)
        if not parent:
            graph.add_requirement(req)
        else:
            graph.add_dependency(parent, req)
        dependencies = dist.requires()
        dists = retriever.get_distributions_with_pkg_resource_requirements(
                dependencies)
        for dist in dists:
            self._collect_dependencies(dist, graph, retriever, parent=req)

class LockedRequirement(object):
    def __init__(self, name, lock_string):
        self._name = name
        self._lock_string = lock_string

    def to_pip_str(self):
        return self._lock_string

class LockedRequirementsParser(object):
    def __init__(self, graph=None):
        self.graph = graph or RequirementsDependencyGraph()

    def create_graph_from_string(self, locked_string):
        from .requirements import Requirement
        self.graph.add_requirement(Requirement('fake1'))
        self.graph.add_dependency(Requirement('fake1'), Requirement('fake2'))

class RequirementsJoiner(object):
    """Joins locked requirements and the requirements set"""
    def __init__(self, locked_string=None, requirement_set=None, 
            locked_string_parser=None):
        self._locked_string = locked_string
        self._requirement_set = requirement_set
        self._locked_string_parser = (locked_string_parser or 
                LockedRequirementsParser())

    def join_to_str(self, requirement_set=None, locked_string=None):
        requirement_strings = []
        if requirement_set:
            requirement_strings = map(lambda a: a.to_pip_str(), 
                    requirement_set)
        locked_display = self.get_locked_display(locked_string)
        locked_display_string = locked_display.show_dependencies(
                requirement_set)
        joined_string = "%s%s" % (locked_display_string, 
                "\n".join(requirement_strings))
        return joined_string

    def get_locked_display(self, locked_string):
        locked_graph, top_level_reqs = (self._locked_string_parser
                .create_graph_from_string(locked_string))
        locked_display = RequirementsGraphDisplay(locked_graph, 
                used=top_level_requirements)
        return locked_display

class RequirementsDependencyGraph(object):
    """An adjacency list storage of the requirements graph

    The requirements are expected to be pip.FrozenRequirement Types
    """
    def __init__(self):
        self._adj_list = {}
        self._requirements = {}

    def add_requirement(self, requirement):
        req_deps = self._adj_list.get(requirement.name.lower())
        if req_deps:
            # Do nothing if the requirement exists already
            return
        self._adj_list[requirement.name.lower()] = []
        self._requirements[requirement.name.lower()] = requirement

    def get_requirement(self, requirement_name):
        """Retrieves a requirement by name"""
        requirement = self._requirements.get(requirement_name.lower())
        return requirement

    def get_dependencies(self, requirement, ignore=None):
        ignore = ignore or []
        requirement = self.resolve_requirement(requirement)
        deps = self._adj_list.get(requirement.name.lower())
        if ignore:
            old_deps = deps[:]
            deps = [dep for dep in old_deps if not dep in ignore]
        return deps

    def get_all_dependencies(self, requirement):
        requirement = self.resolve_requirement(requirement)
        req2 = self.resolve_requirement('fake2')
        req3 = self.resolve_requirement('fake3')
        req4 = self.resolve_requirement('fake4')
        return [req2, req3, req4]

    def resolve_requirement(self, requirement):
        if isinstance(requirement, (str, unicode)):
            req_name = requirement
            requirement = self.get_requirement(req_name)
            if not requirement:
                raise KeyError('Requirement "%s" does not exist in graph' %
                        req_name)
        else:
            # Ensure we are using the current requirement
            requirement = self.get_requirement(requirement.name.lower())
        return requirement

    def add_dependency(self, requirement, dependency_req):
        # Check if the dependency already has it's own storage
        requirement = self.resolve_requirement(requirement)
        check_req = self.get_requirement(dependency_req.name)
        if not check_req:
            self.add_requirement(dependency_req)
        deps = self.get_dependencies(requirement)
        deps.append(dependency_req)

class RequirementsGraphDisplay(object):
    def __init__(self, graph, used=None):
        self.graph = graph
        self.used = used or []

    def show_dependencies(self, requirements, stream=None, 
            comment_doubles=False, used=None):
        stream = stream or StringIO()
        used = used or self.used
        used = self._build_used_list(requirements, used)
        for requirement in requirements:
            requirement = self.graph.resolve_requirement(requirement)
            self._build_dependency_string(requirement, stream, 
                    comment_doubles=comment_doubles, used=used)
        stream.seek(0)
        return stream.read()

    def _build_used_list(self, requirements, used):
        full_used = used[:]
        for requirement in requirements:
            requirement = self.graph.resolve_requirement(requirement)
            full_used.append(requirement.name.lower())
        return full_used

    def _build_dependency_string(self, requirement, stream, level=0, 
            comment_doubles=False, used=None):
        used.append(requirement.name.lower())
        level_str = LEVEL_STR * level
        # Write the current requirement to the stream
        stream.write('%s%s (%s)\n' % (level_str, requirement.name.lower(), 
            requirement.req))
        graph = self.graph
        # Get all of the current dependencies
        deps = graph.get_dependencies(requirement)
        # Recursively add them to the stream
        for dependency in deps:
            self._build_dependency_string(dependency, stream, 
                    level=level+1, used=used)
        return stream
