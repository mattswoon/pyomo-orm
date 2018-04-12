from setuptools import setup

setup(
    name='pyomo-orm',
    version='0.1',
    description='ORM like functionality for Pyomo and SQLAlchemy',
    url='',
    author='mattswoon',
    packages=[
        'pyomo_orm',
        'pyomo_orm.core'
    ],
    install_requires=[
        'SQLAlchemy>=1.2',
        'Pyomo>=5.2'
        'Pandas>=0.22.0'
    ]
)
