import pandas as pd

from pyomo.environ import Set, Param


def create_data_dict(pyomo_model, namespace):
    """
    Creates a dictionary of model data for the given pyomo AbstractModel which
    can used to create a ConcreteModel using create_instance
    """
    pyomo_orm_components = [c for c in pyomo_model.component_objects() if hasattr(c, '_model')]
    di = {}
    for component in pyomo_orm_components:
        if isinstance(component, Set) or isinstance(component, Param):
            this_data = component._model.get_data(
                from_attr=component._from_attr,
                indexed_by=component._indexed_by
            )
            di.update({component.name: this_data})
    return {namespace: di}

def as_dataframe(query):
    """
    Returns the results of a query as a pandas as_dataframe
    """
    return pd.read_sql(query.statement, query.session.bind)
