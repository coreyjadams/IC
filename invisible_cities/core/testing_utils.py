import numpy  as np

from pytest import approx

from numpy.testing          import assert_array_equal, assert_allclose
from hypothesis.strategies  import integers, floats
from hypothesis.extra.numpy import arrays


def exactly(value, **kwargs):
    """
    Assert that two numbers (or two sets of numbers) are equal to each
    other with zero tolerance. This function is intended to have a
    similar behavior to `pytest`'s approx function, but for integers.
    This is particularly interesting when comparing numpy arrays, as
    the expression is less readable:

    ```
    np.all(array1 == array2)
    ```

    to be compared with

    ```
    array1 == exactly(array2)
    ```

    which is more pleasant to the human eye and keeps the symmetry with
    floating point comparisons.
    """
    return approx(value, rel=0, abs=0, **kwargs)


def float_arrays(size       =   100,
                 min_value  = -1e20,
                 max_value  = +1e20,
                 mask       =  None,
                 **kwargs          ):
    elements = floats(min_value,
                      max_value,
                      **kwargs)
    if mask is not None:
        elements = elements.filter(mask)
    return arrays(dtype    = np.float32,
                  shape    =       size,
                  elements =   elements)


def FLOAT_ARRAY(*args, **kwargs):
    return float_arrays(*args, **kwargs).example()


def random_length_float_arrays(min_length =     0,
                               max_length =   100,
                               **kwargs          ):
    lengths = integers(min_length,
                       max_length)

    return lengths.flatmap(lambda n: float_arrays(       n,
                                                  **kwargs))


def _compare_dataframes(assertion, df1, df2, check_types=True, **kwargs):
    assert sorted(df1.columns) == sorted(df2.columns), "DataFrames with different structure cannot be compared"

    for col in df1.columns:
        col1 = df1[col]
        col2 = df2[col]
        if check_types:
            assert col1.dtype == col2.dtype
        print(col, col1.values - col2.values)
        assertion(col1.values, col2.values, **kwargs)


def assert_dataframes_equal(df1, df2, check_types=True, **kwargs):
    _compare_dataframes(assert_array_equal, df1, df2, check_types, **kwargs)


def assert_dataframes_close(df1, df2, check_types=True, **kwargs):
    _compare_dataframes(assert_allclose, df1, df2, check_types, **kwargs)
