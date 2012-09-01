"""
virtstrap.locker
----------------

"""
import sys
import os
import pip
import pkg_resources
import re
import site
import platform
from cStringIO import StringIO

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


def site_packages_dir(base_dir=None):
    """Determines correct site-packages directory. Used when writing lock file

    Works with:
        - CPython 2.6
        - CPython 2.7
        - Pypy-1.7
    """
    # Calculate the default location
    base = base_dir or os.path.realpath(sys.prefix)
    site_packages = os.path.join(base, 'lib',
            'python%s' % sys.version[:3], 'site-packages')
    implementation = platform.python_implementation().lower()
    # Handle any other exceptions
    if implementation == "pypy":
        site_packages = os.path.join(base, 'site-packages')
    return site_packages


class DistributionRetriever(object):
    def __init__(self, sys_path=None, working_set=None):
        self._sys_path = None
        self._working_set = (working_set or
                self.create_work_set())
        if not self._sys_path:
            self._sys_path = sys_path or sys.path

    def create_work_set(self):
        # Virtualenv directory
        # FIXME support windows here
        site_packages = site_packages_dir()
        site.addsitedir(site_packages)
        sys_path = sys.path
        self._sys_path = sys_path
        return pkg_resources.WorkingSet(entries=sys_path)

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
        working_set_dict = working_set.by_key
        working_set_keys = working_set_dict.keys()
        search_list = map(lambda a: (a.lower(), a), working_set_keys)
        real_name = name
        for search_key, real_key in search_list:
            if search_key == name.lower():
                real_name = real_key
        return working_set_dict[real_name]


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
        # Compatibility for pip version < 1.2
        load_version_control = getattr(pip, 'version_control', lambda: None)
        load_version_control()
        # Create a frozen requirement for each installed dist
        dep_graph = RequirementsDependencyGraph()
        retriever = DistributionRetriever()
        dists = retriever.get_distributions(requirement_set)
        for dist in dists:
            self._collect_dependencies(dist, dep_graph, retriever)
        return dep_graph

    def _collect_dependencies(self, dist, graph, retriever, parent=None):
        req = LockedRequirement.from_dist(dist, [], find_tags=False)
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
    @classmethod
    def from_dist(cls, dist, dependency_links, find_tags=False):
        pip_req = pip.FrozenRequirement.from_dist(dist, dependency_links, find_tags=find_tags)
        req_prefix = ''
        if pip_req.editable:
            req_prefix = '-e '
        req_str = str(pip_req.req)
        if req_str.startswith('git:'):
            req_str = 'git+%s' % req_str
        lock_string = '%s%s' % (req_prefix, req_str)
        return cls(pip_req.name.lower(), lock_string)

    def __init__(self, name, lock_string):
        self.name = name
        self._lock_string = lock_string

    def to_pip_str(self):
        return self._lock_string

    def __repr__(self):
        return 'LockedRequirement(%s)' % self.name


class LockedRequirementSet(object):
    """Facade for the Locked Requirements

    Provides a simple interface to the graph that stores locked requirements
    """
    @classmethod
    def from_string(cls, string):
        parser = LockedRequirementsParser()
        graph, top_level_requirements = parser.create_graph_from_string(string)
        return cls(graph, top_level_requirements)

    @classmethod
    def from_file(cls, filename):
        file_obj = open(filename)
        string = file_obj.read()
        return cls.from_string(string)

    def __init__(self, graph, top_level_requirements):
        self._graph = graph
        self._top_level = top_level_requirements

    def display(self, format=None):
        graph_str = RequirementsGraphDisplay.graph_to_str(self._graph,
                self._top_level, display=format)
        return graph_str

    def find(self, name):
        """Find's a requirement by name"""
        return self._graph.get_requirement(name)

    def get_all_dependencies(self, name):
        """Get a requirement's dependencies by name"""
        return self._graph.get_all_dependencies(name)


class LockedRequirementsParser(object):
    def __init__(self, graph=None):
        self.graph = graph or RequirementsDependencyGraph()
        self.top_level = []

    def create_graph_from_string(self, locked_string):
        stream = StringIO(locked_string)
        stream_iter = iter(stream.readlines())
        try:
            self.parse(stream_iter)
        except StopIteration:
            pass
        return self.graph, self.top_level

    def get_graph(self):
        return self.graph

    def parse(self, stream_iter):
        requirement_match = re.compile('([ ]*)(.*) \((.*)\)$')
        last = None
        level = 0
        req_stack = []
        level_str_len = len(LEVEL_STR)

        while True:
            # grab current line
            line = stream_iter.next()
            # match the current line using a regex and get spaces, name, lock_string
            if not line.strip():
                continue
            matches = requirement_match.match(line)
            spaces, name, lock_string = matches.groups()
            # divide the spaces by the LEVEL_STR to get line's level
            line_level = len(spaces) / level_str_len
            # if the line's level is greater than current:
            if line_level > level:
                # increment level
                level += 1
                # add the last item to the req_stack
                req_stack.append(last)
            # if the line's level is less than current:
            if line_level < level:
                # decrement level
                level -= 1
                # pop the last item on the req_stack
                req_stack.pop()
            last = LockedRequirement(name, lock_string)
            # if the req_stack has something:
            if req_stack:
                # add a dependency to the graph (use the last req_stack)
                self.graph.add_dependency(req_stack[-1], last)
            else:
                # if there's no stack we're on level 0
                self.top_level.append(last)
                # add a requirement to the graph
                self.graph.add_requirement(last)


class RequirementsJoiner(object):
    """Joins locked requirements and the requirements set"""
    def __init__(self, locked_string=None, requirement_set=None,
            locked_string_parser=None):
        self._locked_string = locked_string
        self._requirement_set = requirement_set
        self._locked_string_parser = (locked_string_parser or
                LockedRequirementsParser())

    def join_to_str(self, requirement_set=None, locked_string=None):
        locked_display, top_level_reqs = self.get_locked_display(locked_string)
        locked_display_string = locked_display.show_dependencies(
                requirement_set)

        requirement_strings = self.additional_requirements(requirement_set,
                top_level_reqs)

        joined_string = "%s%s" % (locked_display_string,
                "\n".join(requirement_strings))
        return joined_string

    def additional_requirements(self, requirement_set,
            top_level_requirements):
        top_level_names = map(lambda a: a.name.lower(), top_level_requirements)
        requirement_strings = []
        if requirement_set:
            non_locked_requirements = filter(
                    lambda a: not a.name.lower() in top_level_names,
                    requirement_set)
            requirement_strings = map(lambda a: a.to_pip_str(),
                    non_locked_requirements)
        return requirement_strings

    def get_locked_display(self, locked_string):
        def pip_display(level, requirement):
            level_str = LEVEL_STR * level
            return '%s%s\n' % (level_str, requirement.to_pip_str())
        locked_graph, top_level_reqs = (self._locked_string_parser
                .create_graph_from_string(locked_string))
        locked_display = RequirementsGraphDisplay(locked_graph,
                display=pip_display)
        return locked_display, top_level_reqs


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
        all_dependencies = []
        self._collect_dependencies(requirement, all_dependencies)
        return all_dependencies

    def _collect_dependencies(self, requirement, collection, used=None):
        used = used or []
        dependencies = self.get_dependencies(requirement)
        for dependency in dependencies:
            if not dependency.name in used:
                collection.append(dependency)
                used.append(dependency.name)
                self._collect_dependencies(dependency, collection, used=used)

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
    @classmethod
    def graph_to_str(cls, graph, top_level, display=None):
        display = cls(graph, display=None)
        return display.show_dependencies(top_level)

    def __init__(self, graph, display=None):
        self.graph = graph
        self._display = display or self.default_display

    def show_dependencies(self, requirements, stream=None):
        stream = stream or StringIO()
        for requirement in requirements:
            requirement = self.graph.resolve_requirement(requirement)
            if requirement:
                self._build_dependency_string(requirement, stream)
        stream.seek(0)
        return stream.read()

    def _build_dependency_string(self, requirement, stream, level=0):
        # Write the current requirement to the stream
        stream.write(self._display(level, requirement))
        graph = self.graph
        # Get all of the current dependencies
        deps = graph.get_dependencies(requirement)
        # Recursively add them to the stream
        for dependency in deps:
            self._build_dependency_string(dependency, stream,
                    level=level+1)
        return stream

    def default_display(self, level, requirement):
        level_str = LEVEL_STR * level
        lock_string = requirement.to_pip_str()
        return '%s%s (%s)\n' % (level_str, requirement.name.lower(),
                lock_string)
