from sqlalchemy.ext.declarative import declarative_base

from pyomo_orm.core.mixins import BaseModelMixin
from pyomo_orm.core.database import Session
from pyomo_orm.core.exc import ModelDoesNotExist

class DeclarativeBase:
    def __validate__(self):
        """Run all methods which start with validate"""
        methlist = [x for x in dir(type(self)) if callable(getattr(self, x))]
        for meth in methlist:
            if meth.startswith('validate'):
                getattr(self, meth)()

    def save(self):
        """Validate, add and commit model instance to database"""
        self.__validate__()
        s = Session()
        try:
            s.add(self)
            return s.commit()
        except IntegrityError as e:
            raise IntegrityError(
                'Couldn\'t save object {0}: {1}'.format(
                    str(self),
                    str(e)
                ),
                e.params,
                e.orig
            )

    def delete(self):
        s = Session()
        s.delete(self)
        return s.commit()

    @classmethod
    def get(cls, **kwargs):
        ret = cls.query().filter_by(**kwargs).first()
        if ret is not None:
            return ret
        else:
            raise(
                ModelDoesNotExist(
                    'Specified {1} ({0}) does not exist'.format(
                        str(cls),
                        str(kwargs)
                    ),
                    cls
                )
            )

    @classmethod
    def query(cls, *args, **kwargs):
        """Return a sqlalchemy query object for the current model"""
        s = Session()
        return s.query(cls, *args, **kwargs)

    @classmethod
    def load_csv(cls, filename):
        """
        Read data from a csv file and save to the bound database
        Arguments:
            *filename* a path object of the file to be loaded
        CSV Headings:
            the name of the attribute **OR**
            the name of the related table and a Column object of the related
            table separeted with a period (.). The Column in the related table
            should have a unique constraint, and the related table should be present in
            ``__parents__.keys()``
        If data from csv requires special parsing, its column an function parser
        should be entered in the ``__csv_parsers__`` dictionary.
        """
        df = pd.read_csv(filename)
        cls.load_dataframe(df)

    @classmethod
    def load_dataframe(cls, dataframe):
        setattr(DeclarativeBase.load_dataframe.__func__,'__instances_made_with__', [])
        for i, r in dataframe.iterrows():
            model_instance = cls._create_from_csv_row(r)
            model_instance.save()

    @classmethod
    def _create_from_csv_row(cls, row_data):
        module = __import__('nemzord')
        r_dict = {}
        for k, v in row_data.to_dict().items():
            if '.' in k:
                key = k.split('.')[0]
                class_ = getattr(
                    module.models,
                    cls.__parents__[key]
                )
                col = k.split('.')[1]
                val = class_.query().filter_by(**{col: v}).first()
            elif k in cls.__csv_parsers__.keys():
                key = k
                val = cls.__csv_parsers__[k](v)
            else:
                key = k
                val = v
            r_dict[key] = val
        model_instance = cls(**r_dict)
        cls.load_dataframe.__instances_made_with__.append(
            r_dict
        )
        logging.debug('Made {0} instance with {1}'.format(str(cls), str(r_dict)))
        return model_instance

    @classmethod
    def csv_info(cls):
        """
        Return information about the required csv format
        """
        module = __import__('nemzord')
        descriptions = []
        for column in [x for x in cls.__table__.columns if x.primary_key is False]:
            this_description = '{0} ({1})'.format(column.key, str(column.type))
            for fk in column.foreign_keys:
                for name, model in cls.__parents__.items():
                    model_cls = getattr(module.models, model)
                    if fk.references(model_cls.__table__):
                        for c in model_cls._get_unique_columns():
                            this_description += '|{0}.{1} ({2})'.format(
                                name,
                                c.key,
                                str(c.type)
                            )
            descriptions.append(this_description)
        return '\n'.join(descriptions)

    @classmethod
    def _get_unique_columns(cls):
        """Return a list of sqlalchemy.Column objects with a unique constraint"""
        uc = []
        for column in cls.__table__.columns:
            if column.unique is True:
                uc.append(column)
        return uc

    @classmethod
    def get_class_by_tablename(cls, tablename):
        """
        Return class reference mapped to tablename
        """
        for c in cls._decl_class_registry.values():
            if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
                return c

Base = declarative_base(cls=(BaseModelMixin, DeclarativeBase))

def create_all():
    s = Session()
    Base.metadata.create_all(s.connection())
