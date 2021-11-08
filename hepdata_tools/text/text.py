import numpy as np
import scipy.special
from hepdata_tools import fc
from hepdata_tools.types import (
    AsymError,
    AsymErrorValue,
    SymError,
    Header,
    IndependentVariable,
    DependentVariable,
    DataFile,
    Value,
    Bin,
)


def asym_stat_error(x):
    """Generate asymmetrical statistical errors using the Feldman Cousins' method.
    Assuming x is an array of observed counts."""
    min_x, max_x = fc.poisson_interval(x, alpha=scipy.special.erf(1.0 / np.sqrt(2.0)))
    return AsymError(
        AsymErrorValue(minus=float(min_x - x), plus=float(max_x - x)), label="stat"
    )


def sym_stat_error(x):
    """Generate symmetrical statistical error.
    Assuming x is an array of observed counts."""
    return SymError(
        symerror=float(np.sqrt(x)),
        label="stat",
    )


def data_and_bins(
    data_file=None,
    data_name=None,
    bin_file=None,
    bin_name=None,
    data_units="counts per bin",
    bin_units="MeV",
):
    """Generate a DataFile object from binnned data and bin boundaries.
    Assumes counts are integer quantities.
    Generates asymmetric errors."""
    data = np.loadtxt(data_file)
    boundaries = np.loadtxt(bin_file)
    data_values = [Value(int(x), [asym_stat_error(x)]) for x in data]
    bin_values = [
        Bin(low=float(boundaries[i]), high=float(boundaries[i + 1]))
        for i in range(len(boundaries) - 1)
    ]

    indep_header = Header(bin_name, bin_units)
    dep_header = Header(data_name, data_units)

    indep = IndependentVariable(indep_header, bin_values)
    dep = DependentVariable(dep_header, data_values)

    return DataFile([indep], [dep])


def expect_and_bins(
    data_file=None,
    data_name=None,
    bin_file=None,
    bin_name=None,
    data_units="counts per bin",
    bin_units="MeV",
):
    """Generate a DataFile object from binnned simulation and bin boundaries.
    Assumes counts are floating point quantities."""
    data = np.loadtxt(data_file)
    boundaries = np.loadtxt(bin_file)
    data_values = [Value(float(x)) for x in data]
    bin_values = [
        Bin(low=float(boundaries[i]), high=float(boundaries[i + 1]))
        for i in range(len(boundaries) - 1)
    ]

    indep_header = Header(bin_name, bin_units)
    dep_header = Header(data_name, data_units)

    indep = IndependentVariable(indep_header, bin_values)
    dep = DependentVariable(dep_header, data_values)

    return DataFile([indep], [dep])


def cov_and_bins(
    data_file=None,
    data_name=None,
    bin_file=None,
    bin_name=None,
    data_units="counts per bin",
    bin_units="MeV",
):
    """Generate a DataFile object from a covariance matrix and bin boundaries.
    Assumes counts are floating point quantities."""
    data = np.loadtxt(data_file)
    boundaries = np.loadtxt(bin_file)
    cov_values = []
    bin0_values = []
    bin1_values = []
    for i in range(len(boundaries) - 1):
        for j in range(len(boundaries) - 1):
            bin0_values.append(
                Bin(low=float(boundaries[i]), high=float(boundaries[i + 1]))
            )
            bin1_values.append(
                Bin(low=float(boundaries[j]), high=float(boundaries[j + 1]))
            )
            cov_values.append(Value(float(data[i, j])))

    indep_header = Header(bin_name, bin_units)
    dep_header = Header(data_name, data_units)

    indep0 = IndependentVariable(indep_header, bin0_values)
    indep1 = IndependentVariable(indep_header, bin1_values)
    dep = DependentVariable(dep_header, cov_values)

    return DataFile([indep0, indep1], [dep])


def generalized_cov(
    data_file=None,
    data_name=None,
    per_entry_bin_indices=None,  # nxm
    bin_files=None,  # m
    bin_names=None,  # m
    bin_units=None,  # m
    categories=None,  # n
    data_units="counts per bin",
):
    """Generate a DataFile object from a covariance matrix and bin boundaries.
    Assumes counts are floating point quantities."""
    data = np.loadtxt(data_file)

    n_points = len(data)

    if bin_files is None:
        bin_files = []
    n_dims = len(bin_files)
    assert(len(bin_files) == n_dims)
    assert(len(bin_names) == n_dims)
    assert(len(bin_units) == n_dims)

    boundaries = [np.loadtxt(bin_file) for bin_file in bin_files]
    bins = [[Bin(low=float(boundary[i]), high=float(boundary[i + 1])) for i in range(len(boundary)-1)] for boundary in boundaries]
    indep_values = []
    indep_headers = []
    for k in range(n_dims):
        indep_headers.append(Header(bin_names[k], bin_units[k]))
        indep_values.append([(lambda x: Value("") if x is None else bins[k][x])(per_entry_bin_indices[i][k]) for i in range(n_points)])
    if categories is not None:
        assert(len(categories) == n_points)
        cat_header = Header("Category", "")
        n_dims += 1
        indep_headers.append(cat_header)
        indep_values.append([Value(cat) for cat in categories])

    bin_i = []
    bin_j = []
    cross_indep_headers = [Header(h.name + " i", h.units) for h in indep_headers]
    cross_indep_headers += [Header(h.name + " j", h.units) for h in indep_headers]
    cross_indep_values = np.zeros((len(indep_headers) * 2, 0)).tolist()
    cov_values = []
    for i in range(n_points):
        for j in range(n_points):
            bin_i.append(Value(float(i)))
            bin_j.append(Value(float(j)))
            cov_values.append(Value(float(data[i, j])))
            for k in range(n_dims):
                cross_indep_values[k].append(indep_values[k][i])
                cross_indep_values[k + n_dims].append(indep_values[k][j])
    bin_i = IndependentVariable(Header("Bin i", ""), bin_i)
    bin_j = IndependentVariable(Header("Bin j", ""), bin_j)
    cross_indeps = [bin_i, bin_j] + [IndependentVariable(header, values) for header, values in zip(cross_indep_headers, cross_indep_values)]

    dep_header = Header(data_name, data_units)
    dep = DependentVariable(dep_header, cov_values)

    return DataFile(cross_indeps, [dep])


def ntuple(fname=None, column_names=None, column_units=None, is_independent=None):
    """Generate a DataFile object from an ntuple.
    Assumes data points are floating point quantities."""
    data = np.loadtxt(fname)
    n = max(len(column_names), len(column_units), len(is_independent))
    names = [column_names[i] if i < len(column_names) else "" for i in range(n)]
    units = [column_units[i] if i < len(column_units) else "" for i in range(n)]
    indep = [is_independent[i] if i < len(is_independent) else True for i in range(n)]

    deps = []
    indeps = []

    for i, (name, unit, is_indep) in enumerate(zip(names, units, indep)):
        header = Header(name, unit)
        values = [Value(float(x)) for x in data[:, i]]
        if is_indep:
            indeps.append(IndependentVariable(header, values))
        else:
            deps.append(DependentVariable(header, values))

    return DataFile(indeps, deps)
