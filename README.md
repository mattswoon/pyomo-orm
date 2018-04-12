# Overview

pyomo-orm uses SQLAlchemy to add ORM-like data handling for Pyomo.

# Purpose

Often when creating mathematical models we want to structure our model
formulation and data similarly as the formulation of the optimisation problem
is often inspired by the structure of the input data, or vice versa.

Mathematical optimisation frameworks like Pyomo provide an elegant way of
formulating optimisation problems and solving them, but offer little in the way
of managing and maintaining data.

Object Relational Mappings (ORM) like that provided with SQLAlchemy are
an useful tool for managing and accessing data stored in databases.

This project provides a way to combine SQLAlchemy's ORM and Pyomo's mathematical
language into a single, unified package so that mathematical models and their
data can be created in a simple and transparent way.

## A note on language

We often want to use the word 'model' to refer both to mathematical models
and data models used by the ORM. This has the possibility to create confusion.
Here we use the word 'problem' to refer to a mathematical model as we are
specifically concerned with those mathematical models that are formulated as an
optimisation problem. Further, we 'solve' 'problems', not 'models'.

# Goals

## Simple to use

As we often structure data and problems in a similar fashion they should follow
similar code layouts, which are easy to read.

## Transparent problems

It should be easy for an analyst to determine what input data generated which
set of solutions with which problem formulation.
