from pyomo.environ import Set

from .base import ORMComponent

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
            self._problem().pyomo_model,
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
            self._problem().pyomo_model,
            from_attr=self.from_attr,
            indexed_by=self.indexed_by,
            queryset=self.queryset,
            **self._kwargs
        )
