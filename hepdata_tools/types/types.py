import numpy as np
import typing
import scipy.special
from hepdata_tools import fc
from . import type_utils


# Header file yaml doc
class Header(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    name: str
    units: str


class AsymErrorValue(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    minus: typing.Union[float, int]
    plus: typing.Union[float, int]


class AsymError(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    asymerror: AsymErrorValue
    label: typing.Union[None, str] = None


class SymError(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    symerror: typing.Union[float, int]
    label: typing.Union[None, str] = None


class Value(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    value: typing.Union[float, int, str]
    errors: typing.Union[None, typing.List[typing.Union[SymError, AsymError]]] = None


class Bin(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    low: typing.Union[float, int]
    high: typing.Union[float, int]


class Qualifier(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    name: str
    value: typing.Union[float, int, str]
    units: typing.Union[None, str] = None


class DependentVariable(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    header: Header
    values: typing.Union[None, typing.List[Value]] = None
    qualifiers: typing.Union[None, typing.List[Qualifier]] = None


class IndependentVariable(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    header: Header
    values: typing.Union[typing.List[Value], typing.List[Bin]]


class DataFile(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    independent_variables: typing.List[IndependentVariable]
    dependent_variables: typing.List[DependentVariable]


# Submission file yaml doc


class Keyword(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    name: str
    values: typing.List[typing.Union[str, float, int]]


class License(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    name: str
    url: str
    description: str


class AdditionalResource(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    description: str
    location: str
    license: typing.Union[None, License] = None


class LinkedResource(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    name: str
    description: str
    keywords: typing.Union[typing.List[Keyword]]
    location: typing.Union[None, str] = None
    data_file: typing.Union[None, str] = None
    data_license: typing.Union[None, License] = None
    additional_resources: typing.Union[None, typing.List[AdditionalResource]] = None


class InlineResource(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    name: str
    description: str
    keywords: typing.List[Keyword]
    location: typing.Union[None, str] = None
    independent_variables: typing.Union[None, typing.List[IndependentVariable]] = None
    dependent_variables: typing.Union[None, typing.List[DependentVariable]] = None
    data_license: typing.Union[None, License] = None
    additional_resources: typing.Union[None, typing.List[AdditionalResource]] = None


class Submission(type_utils.TypeCheck, metaclass=type_utils.NamedTupleMeta):
    additional_resources: typing.List[typing.Union[AdditionalResource]]
    comment: str
