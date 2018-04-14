from .orm_components import ORMConstraint, ORMObjective

def orm_constraint(*index_sets, **kwargs):
    def decorator(func):
        return ORMConstraint(*index_sets, rule=func, **kwargs)
    return decorator

def orm_objective(*index_sets, **kwargs):
    def decorator(func):
        return ORMObjective(*index_sets, rule=func, **kwargs)
    return decorator
