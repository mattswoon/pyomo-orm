from pyomo.environ import Set, Param
from .database import Session

class BaseModelMixin:
    """
    Mixin to add pyomo features to models
    """

    @classmethod
    def create_set(cls, from_attr='id', indexed_by=None, **kwargs):
        s = Set(**kwargs)
        s._model = cls
        s._from_attr = from_attr
        s._indexed_by = indexed_by
        return s

    @classmethod
    def create_param(cls, pyomo_model, from_attr='id', indexed_by=None, **kwargs):
        dispatcher = {
            type(None): cls._create_noindex_param,
            str: cls._create_index_param,
            tuple: cls._create_multiindex_param
        }
        return dispatcher[type(indexed_by)](pyomo_model, from_attr, indexed_by, **kwargs)

    @classmethod
    def _create_index_param(cls, pyomo_model, from_attr, indexed_by, **kwargs):
        index_sets = cls._infer_index_set(pyomo_model, indexed_by)
        p = Param(*index_sets, **kwargs)
        p._from_attr = from_attr,
        p._indexed_by = indexed_by
        p._model = cls
        return p

    @classmethod
    def _create_multiindex_param(cls, pyomo_model, from_attr, indexed_by, **kwargs):
        index_sets = cls._infer_multiindex_set(pyomo_model, indexed_by)
        p = Param(*index_sets, **kwargs)
        p._from_attr = from_attr,
        p._indexed_by = indexed_by
        p._model = cls
        return p

    @classmethod
    def _create_noindex_param(cls, pyomo_model, from_attr, indexed_by, **kwargs):
        p = Param(**kwargs)
        p._indexed_by = indexed_by
        p._from_attr = from_attr
        p._model = cls
        return p

    @classmethod
    def _infer_index_set(cls, pyomo_model, indexed_by):
        """
        Retrieves a list of the sets defined in pyomo_model that were created by
        pyomo-orm that match the column of cls named 'indexed_by'.

        Assumes indexed_by is a string
        """
        inferred_sets = []
        orm_created_sets = [c for c in pyomo_model.component_objects() if hasattr(c, '_model') and isinstance(c, Set)]
        for s in orm_created_sets:
            if s._model == cls and s._from_attr == indexed_by:
                inferred_sets.append(s)
        return inferred_sets

    @classmethod
    def _infer_multiindex_set(cls, pyomo_model, indexed_by):
        """
        Retrieves a list of the sets defined in pyomo_model that were created by
        pyomo-orm that match the column of each element in the 'indexed_by' tuple,
        following foreign keys if present
        """
        inferred_sets = []
        orm_created_sets = [c for c in pyomo_model.component_objects() if hasattr(c, '_model') and isinstance(c, Set)]
        for ind in indexed_by:
            for s in orm_created_sets:
                if s._model == cls and s._from_attr == ind:
                    inferred_sets.append(s)
                for fk in getattr(cls.__table__.c, ind).foreign_keys:
                    tablename = fk.target_fullname.split('.')[0]
                    column_name = fk.target_fullname.split('.')[1]
                    model = cls.get_class_by_tablename(tablename)
                    if s._model == model and s._from_attr == column_name:
                        inferred_sets.append(s)
        return inferred_sets

    @classmethod
    def get_data(cls, from_attr='id', indexed_by=None):
        dispatcher = {
            type(None): cls._get_data_noindex,
            str: cls._get_data_index,
            tuple: cls._get_data_multiindex
        }
        return dispatcher[type(indexed_by)](from_attr, indexed_by)

    @classmethod
    def _get_data_noindex(cls, from_attr, indexed_by):
        di = {None: [getattr(m, from_attr) for m in cls.query().all()]}
        return di

    @classmethod
    def _get_data_index(cls, from_attr, indexed_by):
        di = dict(
            [
                (
                    getattr(m, indexed_by),
                    getattr(m, from_attr)
                ) for m in cls.query().all()
            ]
        )
        return di

    @classmethod
    def _get_data_multiindex(cls, from_attr, indexed_by):
        di = dict(
            [
                (
                    tuple([getattr(m, ind) for ind in indexed_by]),
                    getattr(m, from_attr)
                ) for m in cls.query().all()
            ]
        )
        return di
