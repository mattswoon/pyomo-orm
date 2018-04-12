import weakref


class ORMComponent:
    """
    Base class of all ORM components.

    Arguments:
        * index_orm_sets - list of strings of set names belonging to the parent Problem:
            ORMSets that index the component
        * model: the ORM model from which the component is derived
        * from_attr: the column from which to get the data
        * indexed_by: the column which indexes the component. If index_orm_sets
            are also provided the values of the indexed_by column must appear
            in the ORMSets in the index_orm_sets. Defaults to id
        * queryset: The query to use on the ORM model to define the index set
            data. Only one of queryest and index_orm_sets are required
        * pyomo component kwargs: kwargs to pass on to pyomo when creating the
            component
    """
    def __init__(
        self,
        *index_orm_sets,
        model=None,
        from_attr=None,
        indexed_by='id',
        queryset=None,
        **kwargs
    ):
        self._index_orm_set_names = index_orm_sets
        self.model = model
        self.from_attr = from_attr
        self.indexed_by = indexed_by
        self.queryset = queryset
        self._kwargs = kwargs
        self._problem_object = None

    @property
    def _problem(self):
        if self._problem_object is not None:
            return self._problem_object
        else:
            raise AttributeError('Problem object has not been set')

    @_problem.setter
    def _problem(self, value):
        self._problem_object = weakref.ref(value)

    @property
    def index_orm_sets(self):
        ret = []
        for set_name in self._index_orm_set_names:
            if hasattr(self._problem, set_name) and set_name in self._problem.orm_sets:
                ret.append(self._problem.orm_sets[set_name])
        return ret

    @property
    def object_list(self):
        """
        Returns the list of ORM objects referred to by this component
        """
        return self.queryset.all()

    @property
    def problem_data(self):
        """
        Returns the problem data from the model
        """
        return self.model.problem_data(
            from_attr=self.from_attr,
            indexed_by=self.indexed_by,
            queryset=self.queryset
        )
