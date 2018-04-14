from pyomo.environ import Constraint, Objective

from .base import ORMComponent, BaseORMWrapper

class ORMSet(ORMComponent):
    @property
    def pyomo_set(self):
        """
        Returns the pyomo set
        """
        return self.model.create_set(
            from_attr=self.from_attr,
            indexed_by=self.indexed_by,
            queryset=self.queryset,
            **self._kwargs
        )


class ORMParam(ORMComponent):
    @property
    def pyomo_param(self):
        """
        Returns the pyomo Param
        """
        return self.model.create_param(
            *self.index_pyomo_sets,
            from_attr=self.from_attr,
            indexed_by=self.indexed_by,
            queryset=self.queryset,
            **self._kwargs
        )

class ORMVar(ORMComponent):
    @property
    def pyomo_var(self):
        """
        Returns the pyomo Var
        """
        return self.model.create_var(
            *self.index_pyomo_sets,
            from_attr=self.from_attr,
            indexed_by=self.indexed_by,
            queryset=self.queryset,
            **self._kwargs
        )

class ORMRuleBase(BaseORMWrapper):
    """
    Base class to wrap pyomo constraints and objectives. Calling an instance
    will call the rule that gets passed in
    """
    def __init__(self, *index_orm_sets, rule=None, **kwargs):
        super().__init__(*index_orm_sets)
        self.rule = rule
        self._kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return self.rule(*args, **kwargs)


class ORMConstraint(ORMRuleBase):
    """
    A wrapper for constraints. It acts as a container for the index_pyomo_sets as
    a list of their names and a rule function. Calling an instance of an
    ORMConstraint will call the rule.
    """
    @property
    def pyomo_constraint(self):
        return Constraint(
            *self.index_pyomo_sets,
            rule=self.rule,
            **self._kwargs
        )

class ORMObjective(ORMRuleBase):
    """
    A wrapper for objectives. It acts as a container for the index_pyomo_sets as
    a list of their names and a rule function. Calling an instance of an
    ORMObjective will call the rule.
    """
    @property
    def pyomo_objective(self):
        return Objective(
            *self.index_pyomo_sets,
            rule=self.rule,
            **self._kwargs
        )
