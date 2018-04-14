from pyomo.environ import Set, Param, Var
from .database import Session


class BaseModelMixin:
    """
    Mixin to add pyomo features to models
    """

    @classmethod
    def create_set(cls, from_attr='id', indexed_by=None, queryset=None, **kwargs):
        s = Set(**kwargs)
        s._model = cls
        s._from_attr = from_attr
        s._indexed_by = indexed_by
        if queryset is None:
            queryset = cls.query()
        s._model_ids = [x.id for x in queryset.all()]
        return s

    @classmethod
    def create_param(cls, *index_sets, from_attr='id', indexed_by=None, queryset=None, **kwargs):
        p = Param(*index_sets, **kwargs)
        p._from_attr = from_attr
        p._indexed_by = indexed_by
        p._model = cls
        if queryset is None:
            queryset = cls.query()
        p._model_ids = [x.id for x in queryset.all()]
        return p

    @classmethod
    def create_var(cls, *index_sets, from_attr='id', indexed_by=None, queryset=None, **kwargs):
        v = Var(*index_sets, **kwargs)
        v._from_attr = from_attr
        v._indexed_by = indexed_by
        v._model = cls
        if queryset is None:
            queryset = cls.query()
        v._model_ids = [x.id for x in queryset.all()]
        return v

    @classmethod
    def infer_index_set(cls, pyomo_model, indexed_by):
        """
        Returns a list of pyomo sets attached to pyomo_model that
        were created by pyomo-orm and match the indexed_by columns
        """
        dispatcher = {
            type(None): lambda x: [],
            str: cls._infer_index_set,
            tuple: cls._infer_multiindex_set,
            list: cls._infer_multiindex_set
        }
        return dispatcher[type(indexed_by)](pyomo_model, indexed_by)

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
    def get_data(cls, from_attr='id', indexed_by=None, queryset=None):
        if queryset is None:
            queryset=cls.query()
        dispatcher = {
            type(None): cls._get_data_noindex,
            str: cls._get_data_index,
            tuple: cls._get_data_multiindex,
            list: cls._get_data_multiindex
        }
        return dispatcher[type(indexed_by)](from_attr, indexed_by, queryset)

    @classmethod
    def _get_data_noindex(cls, from_attr, indexed_by, queryset):
        if queryset.filter(getattr(cls, from_attr) != None).count() > 1:
            di = {None: [getattr(m, from_attr) for m in queryset.filter(getattr(cls, from_attr) != None).all()]}
        else:
            di = {None: getattr(m, from_attr) for m in queryset.filter(getattr(cls, from_attr) != None).all()}
        return di

    @classmethod
    def _get_data_index(cls, from_attr, indexed_by, queryset):
        di = dict(
            [
                (
                    getattr(m, indexed_by),
                    getattr(m, from_attr)
                ) for m in queryset.all() if getattr(m, from_attr) is not None
            ]
        )
        return di

    @classmethod
    def _get_data_multiindex(cls, from_attr, indexed_by, queryset):
        di = dict(
            [
                (
                    tuple([getattr(m, ind) for ind in indexed_by]),
                    getattr(m, from_attr)
                ) for m in queryset.all() if getattr(m, from_attr) is not None
            ]
        )
        return di
