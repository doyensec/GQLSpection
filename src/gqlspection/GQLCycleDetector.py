from gqlspection import log

class GQLCycleDetector(object):
    """
    A class for detecting cycles in a GraphQL schema.

    Args:
        schema (GraphQLSchema): The GraphQL schema to analyze.
        max_depth (int, optional): The maximum depth to traverse. Defaults to 100.
    """
    def __init__(self, schema, max_depth=100):
        self.schema = schema
        self.max_depth = max_depth
        self.visited = set()
        self.visiting = []
        self.cycles = []

    def _potential_objects(self, gqltype):
        """Get potential objects for the given type."""
        if gqltype.kind.kind == 'OBJECT':
            return [gqltype]
        elif gqltype.kind.kind == 'UNION':
            return (obj for obj in gqltype.unions)
        else:
            return []

    def detect(self):
        """
        Detect cycles in the GraphQL schema.

        This method traverses the schema starting from the query and mutation fields
        and detects any cycles in the schema.
        """
        for field in self.schema.query.fields:
            log.debug("Looking at query field {}".format(field.name))
            for gqltype in self._potential_objects(field.type):
                log.debug("Test type name: {}".format(gqltype.name))
                self._detect_cycle(field.name, gqltype)
                self.visiting = []
                self.visited.clear()
        for field in self.schema.mutation.fields:
            log.debug("Looking at mutation field {}".format(field.name))
            for gqltype in self._potential_objects(field.type):
                log.debug("Test type name: {}".format(gqltype.name))
                self._detect_cycle(field.name, gqltype)
                self.visiting = []
                self.visited.clear()

    def _detect_cycle(self, field_name, gqltype, current_depth=0):
        """
        Detect cycles starting from the given field and GraphQL type.

        Args:
            field_name (str): The name of the field.
            gqltype (GraphQLType): The GraphQL type to analyze.
            current_depth (int, optional): The current depth of the traversal. Defaults to 0.

        Returns:
            bool: True if a cycle is detected, False otherwise.
        """
        self.visited.add((field_name, gqltype.name))
        self.visiting.append((field_name, gqltype.name))

        for field in gqltype.fields:
            for next_gqltype in self._potential_objects(field.type):
                if (field.name, next_gqltype.name) not in self.visited:
                    if current_depth >= self.max_depth:
                        log.error("Max recursion depth reached ({}). Aborting.".format(current_depth))
                        return False
                    if self._detect_cycle(field.name, next_gqltype, current_depth=(current_depth + 1)):
                        return True
                elif (field.name, next_gqltype.name) in self.visiting:
                    cycle_nodes = self.visiting + [(field.name, next_gqltype.name)]
                    self.cycles.append(cycle_nodes)
                    return True
        self.visiting.pop()
        return False

    def print_cycles(self):
        print(self.cycles_as_string())

    def _cycle_as_string(self, cycle):
        return ' -> '.join(['{} ({})'.format(field, gqltype) for field, gqltype in cycle])

    def cycles_as_string(self):
        return '\n'.join([self._cycle_as_string(cycle) for cycle in self.cycles])
