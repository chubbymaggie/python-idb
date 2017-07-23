import os
import os.path

import pytest

import idb


try:
    import capstone
    no_capstone = False
except:
    no_capstone = True


CD = os.path.dirname(__file__)


@pytest.yield_fixture
def empty_idb():
    path = os.path.join(CD, 'data', 'empty', 'empty.idb')
    with idb.from_file(path) as db:
        yield db


@pytest.yield_fixture
def kernel32_idb():
    path = os.path.join(CD, 'data', 'v6.95', 'x32', 'kernel32.idb')
    with idb.from_file(path) as db:
        yield db


@pytest.yield_fixture
def small_idb():
    path = os.path.join(CD, 'data', 'small', 'small-colored.idb')
    with idb.from_file(path) as db:
        yield db


@pytest.yield_fixture
def compressed_idb():
    path = os.path.join(CD, 'data', 'compressed', 'kernel32.idb')
    with idb.from_file(path) as db:
        yield db


@pytest.yield_fixture
def compressed_i64():
    path = os.path.join(CD, 'data', 'compressed', 'kernel32.i64')
    with idb.from_file(path) as db:
        yield db


def load_idb(path):
    with open(path, 'rb') as f:
        return idb.from_buffer(f.read())


def xfail(*spec):
    return ('xfail', spec)


def skip(*spec):
    return ('skip', spec)


COMMON_FIXTURES = {
    (695, 32): load_idb(os.path.join(CD, 'data', 'v6.95', 'x32', 'kernel32.idb')),
    (695, 64): load_idb(os.path.join(CD, 'data', 'v6.95', 'x64', 'kernel32.i64')),
    (700, 32): load_idb(os.path.join(CD, 'data', 'v7.0b', 'x32', 'kernel32.idb')),
    (700, 64): load_idb(os.path.join(CD, 'data', 'v7.0b', 'x64', 'kernel32.i64')),
}


def kern32_test(specs=None):
    '''
    Example::

        @kern32_test([
                 (695, 32, 'bar'),
                 (695, 64, 'bar'),
            xfail(700, 32, 'bar'),
        ])
        def test_foo(kernel32_idb, version, bitness, expected):
            assert 'bar' == expected
    '''
    if specs is None:
        specs = [
            (695, 32, None),
            (695, 64, None),
            (700, 32, None),
            (700, 64, None),
        ]

    ids = []
    params = []

    for spec in specs:
        if spec[0] == 'xfail':
            marks = pytest.mark.xfail
            spec = spec[1]
        elif spec[0] == 'skip':
            marks = pytest.mark.skip
            spec = spec[1]
        else:
            marks = None

        version = spec[0]
        bitness = spec[1]
        expected = spec[2]

        sversion = {
            695: 'v6.95',
            700: 'v7.0b',
        }[version]

        sbitness, filename = {
            32: ('x32', 'kernel32.idb'),
            64: ('x64', 'kernel32.i64'),
        }[bitness]

        if (version, bitness) in COMMON_FIXTURES:
            db = COMMON_FIXTURES[(version, bitness)]
        else:
            path = os.path.join(CD, 'data', sversion, sbitness, filename)
            db = load_idb(path)

        if marks:
            params.append(pytest.param(db, version, bitness, expected, marks=marks))
        else:
            params.append(pytest.param(db, version, bitness, expected))

        ids.append(sversion + '/' + sbitness)

    return pytest.mark.parametrize('kernel32_idb,version,bitness,expected', params, ids=ids)


requires_capstone = pytest.mark.skipif(no_capstone, reason='capstone not installed')
