from pyomo.environ import AbstractModel, SolverFactory

from pyomo_orm.core.models import ProblemRun, ProblemDetail
from pyomo_orm.core.wrappers import ORMComponent, ORMSet, ORMParam, ORMVar

class BaseProblem:
    """
    A base class to make optimisation problems from. BaseProblem provides
    useful methods for recording details regarding solves
    (via the Problem* models) and which components were built using pyomo_orm
    """
    __solver__ = 'cbc'

    def __init__(self, name, description='', version=''):
        self.pyomo_model = AbstractModel()
        self.name = name
        self.namespace = '{}_namespace'.format(name)
        self.description = description
        self.version = version
        self.problem_detail = None
        self._set_component_problems()

    def _set_component_problems(self):
        for attr in dir(type(self)):
            if isinstance(getattr(type(self), attr), ORMComponent):
                setattr(getattr(self, attr), '_problem', self)

    def define_problem(self):
        self.define_sets()
        self.define_params()
        self.define_vars()
        self.define_constraints()
        self.define_objective()

    def define_sets(self):
        """
        Runs create_set on all ORMSets and sets them to self.pyomo_model
        """
        for name, orm_set in self.orm_sets.items():
            setattr(
                self.pyomo_model,
                name,
                orm_set.pyomo_set
            )


    def define_params(self):
        """
        Runs create_param on all ORMParams and sets them to self.pyomo_model
        """
        for name, orm_param in self.orm_params.items():
            setattr(
                self.pyomo_model,
                name,
                orm_param.pyomo_param
            )

    def define_vars(self):
        """
        Runs create_var on all ORMVars and sets them to self.pyomo_model
        """
        for name, orm_var in self.orm_vars.items():
            setattr(
                self.pyomo_model,
                name,
                orm_var.pyomo_var
            )

    def define_constraints(self):
        pass

    def define_objective(self):
        pass

    def create_instance(self, *args, **kwargs):
        """
        Creates an instance of a ConcreteModel from the AbstractModel
        stored in self.pyomo_model. Unless otherwise specified, uses the data
        dictionary created with self.create_problem_data and the namespace
        stored with self.namespace.

        Returns: instance of a ConcreteModel
        """
        if 'data' not in kwargs:
            kwargs.update({'data':self.data})
        if 'namespace' not in kwargs:
            kwargs.update({'namespace':self.namespace})
        instance = self.pyomo_model.create_instance(*args, **kwargs)
        self.instance = instance
        return self.instance

    def create_solver(self, *args, **kwargs):
        """
        Creates a solver using pyomo.environ.SolverFactory. Unless otherwise
        specified, uses self.__solver__

        Returns: solver object
        """
        if not args:
            args = [self.__solver__]
        solver = SolverFactory(*args, **kwargs)
        self.solver = solver
        return self.solver

    def solve(self, **kwargs):
        """
        Solves the problem self.instance and records the solve and the results
        in the relevant Models.

        Returns: solve results as a dict
        """
        results = self.solver.solve(self.instance, **kwargs)
        self._record_solve(results)
        return results

    def _record_solve(self, results):
        """
        Records a solve by
            * creating a ProblemDetail object for the problem if one
            does not already exist
            * creating a ProblemRun object for this solve
            * associating the ProblemRun with all used models via their
            problem_run foreign key
        """
        if self.problem_detail is None:
            self.problem_detail = ProblemDetail(
                name=self.name,
                description=self.description,
                version=self.version
            )
        this_problem_run = ProblemRun(problem_details=self.problem_detail)
        self.current_problem_run = this_problem_run

        # add this_problem_run to all pertinent models
        model_objects_used_in_problem = self._pyomo_orm_instance_components
        for obj in model_objects_used_in_problem:
            obj.problem_run = this_problem_run


    @property
    def _pyomo_orm_abstractmodel_components(self):
        """
        Returns a list of component_objects in the pyomo_model that were created
        by pyomo_orm (i.e. have the attr '_model')
        """
        return [c for c in self.pyomo_model.component_objects() if hasattr(c, '_model')]

    @property
    def _pyomo_orm_instance_components(self):
        """
        Returns a python set of Model objects that have been used to create
        component_objects and give them data in the pyomo_model
        """
        pyomo_orm_components = self._pyomo_orm_abstractmodel_components
        object_list = []
        for c in pyomo_orm_components:
            object_list.append(
                c._model.query().filter(
                    getattr(c._model, c._from_attr).in_(list(c))
                )
            )
        return set(object_list)

    def _get_orm_components(self, orm_component_type):
        ret = {}
        for attr in dir(type(self)):
            if isinstance(getattr(type(self), attr), orm_component_type):
                ret[attr] = getattr(self, attr)
        return ret

    @property
    def orm_sets(self):
        return self._get_orm_components(ORMSet)

    @property
    def orm_params(self):
        return self._get_orm_components(ORMParam)

    @property
    def orm_vars(self):
        return self._get_orm_components(ORMVar)
