"""
virtstrap.joined
~~~~~~~~~~~~~~~~

Handles the Joined Requirements like a RequirementSet

"""
class JoinedRequirementSet(object):
    @classmethod
    def join(cls, requirement_set, locked_graph):
        return cls(requirement_set, locked_graph)

    def __init__(self, requirement_set, locked_graph):
        self._requirement_set = requirement_set
        self._locked_graph = locked_graph

    def as_list(self):
        # Given the requirement set
        locked_graph = self._locked_graph
        joined_list = []
        # The top level requirements are all technically in "use"
        # This prevents duplication in the list
        used = map(lambda a: a.name, self._requirement_set)

        # Loop through the requirements and get all the current locked dependencies
        for requirement in self._requirement_set:
            # See if the top level requirement is in the lock
            locked_requirement = locked_graph.find(requirement.name)
            # If the lock does not exist just put the requirement in the list
            if not locked_requirement:
                joined_list.append(requirement)
                continue
            # If the lock does exist add the lock to the list
            joined_list.append(locked_requirement)
            # Gather all the children for a particular requirement
            for child_requirement in locked_graph.get_all_dependencies(locked_requirement.name):
                # Do not grab duplicates at all
                if not child_requirement.name in used:
                    joined_list.append(child_requirement)
                    used.append(child_requirement.name)
        return joined_list

