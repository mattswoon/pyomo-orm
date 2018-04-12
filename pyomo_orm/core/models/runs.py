from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from pyomo_orm.core.models import Base


class ProblemRunMixin:
    @declared_attr
    def problem_run_id(cls):
        return Column(Integer, ForeignKey('problem_runs.id'), nullable=True)

    @declared_attr
    def problem_run(cls):
        return relationship('ProblemRun')


class ProblemRun(Base):
    __tablename__ = 'problem_runs'

    id = Column(Integer, primary_key=True)
    problem_details_id = Column(Integer, ForeignKey('problem_details.id'))

    problem_details = relationship('ProblemDetail', back_populates='runs')

    def __repr__(self):
        return '<ProblemRun: {problem_name} run_id={id}>'.format(
            problem_name=self.problem_details.name,
            id=self.id
        )

class ProblemDetail(Base):
    __tablename__ = 'problem_details'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    version = Column(String)
    runs = relationship('ProblemRun')

    def __repr__(self):
        return '<ProblemDetail: {name} {version}>'.format(
            name=self.name,
            version=self.version
        )
