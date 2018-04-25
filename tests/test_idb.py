import pytest
import binascii

from fixtures import *

import idb.netnode
import idb.fileformat


slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)


def h2b(somehex):
    '''
    convert the given hex string into bytes.

    binascii.unhexlify is many more characters to type :-).
    '''
    return binascii.unhexlify(somehex)


def b2h(somebytes):
    '''
    convert the given bytes into a hex *string*.

    binascii.hexlify returns a bytes, which is slightly annoying.
    also, its many more characters to type.
    '''
    return binascii.hexlify(somebytes).decode('ascii')


def h(number):
    '''
    convert a number to a hex representation, with no leading '0x'.

    Example::

        assert h(16)   == '10'
        assert hex(16) == '0x10'
    '''
    return '%02x' % number


@kern32_test([
    (695, 32, 4),
    (695, 64, 8),
    (700, 32, 4),
    (700, 64, 8),
])
def test_wordsize(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.wordsize == expected


@kern32_test([
    (695, 32, None),
    (695, 64, None),
    (700, 32, None),
    (700, 64, None),
])
def test_validate(kernel32_idb, version, bitness, expected):
    # should be no ValueErrors here.
    assert kernel32_idb.validate() is True


def do_test_compressed(db):
    for section in db.sections:
        if section is None:
            continue
        assert section.header.is_compressed is True
        assert section.header.compression_method == idb.fileformat.COMPRESSION_METHOD.ZLIB

    # should be no ValueErrors here.
    assert db.validate() is True


def test_compressed(compressed_idb, compressed_i64):
    do_test_compressed(compressed_idb)
    do_test_compressed(compressed_i64)


@kern32_test([
    (695, 32, b'IDA1'),
    (695, 64, b'IDA2'),
    (700, 32, b'IDA1'),
    (700, 64, b'IDA2'),
])
def test_header_magic(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.header.signature == expected
    assert kernel32_idb.header.sig2 == 0xAABBCCDD


@kern32_test([
    (695, 32, 0x2000),
    (695, 64, 0x2000),
    (700, 32, 0x2000),
    (700, 64, 0x2000),
])
def test_id0_page_size(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.id0.page_size == expected


@kern32_test([
    (695, 32, 0x1),
    (695, 64, 0x1),
    (700, 32, 0x1),
    (700, 64, 0x1),
])
def test_id0_root_page(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.id0.root_page == expected


@kern32_test([
    # collected empirically
    (695, 32, 1592),
    (695, 64, 1979),
    (700, 32, 1566),
    (700, 64, 1884),
])
def test_id0_page_count(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.id0.page_count == expected


@kern32_test([
    # collected empirically
    (695, 32, 422747),
    (695, 64, 422753),
    (700, 32, 426644),
    (700, 64, 426647),
])
def test_id0_record_count(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.id0.record_count == expected


@kern32_test([
    (695, 32, None),
    (695, 64, None),
    (700, 32, None),
    (700, 64, None),
])
def test_id0_root_entries(kernel32_idb, version, bitness, expected):
    '''
    Args:
      expected: ignored
    '''
    for entry in kernel32_idb.id0.get_page(kernel32_idb.id0.root_page).get_entries():
        assert entry.key is not None


@kern32_test([
    (695, 32, '24204d4158204c494e4b'),
    (695, 64, '24204d4158204c494e4b'),
    (700, 32, '24204d4158204c494e4b'),
    (700, 64, '24204d4158204c494e4b'),
])
def test_cursor_min(kernel32_idb, version, bitness, expected):
    # test cursor movement from min key
    # min leaf keys:
    #   24204d4158204c494e4b
    #   24204d4158204e4f4445
    #   24204e45542044455343
    #   2e0000000044689ae208
    minkey = kernel32_idb.id0.get_min().key
    assert minkey == h2b(expected)

    cursor = kernel32_idb.id0.find(minkey)
    cursor.next()
    assert b2h(cursor.key) == '24204d4158204e4f4445'
    cursor.prev()
    assert b2h(cursor.key) == '24204d4158204c494e4b'
    with pytest.raises(IndexError):
        cursor.prev()


@kern32_test([
    (695, 32, '4e776373737472'),
    (695, 64, '4e776373737472'),
    (700, 32, '4e776373737472'),
    (700, 64, '4e776373737472'),
])
def test_cursor_max(kernel32_idb, version, bitness, expected):
    # test cursor movement from max key
    # max leaf keys:
    #   4e7763736e636d70
    #   4e7763736e637079
    #   4e7763736e6370795f73
    #   4e77637372636872
    #   4e776373737472
    maxkey = kernel32_idb.id0.get_max().key
    assert maxkey == h2b(expected)

    cursor = kernel32_idb.id0.find(maxkey)
    cursor.prev()
    assert b2h(cursor.key) == '4e77637372636872'
    cursor.next()
    assert b2h(cursor.key) == '4e776373737472'
    with pytest.raises(IndexError):
        cursor.next()


@kern32_test([
    (695, 32, None),
    (700, 32, None),
])
def test_find_exact_match1(kernel32_idb, version, bitness, expected):
    # this is found in the root node, first index
    key = h2b('2e6892663778689c4fb7')
    assert kernel32_idb.id0.find(key).key == key
    assert b2h(kernel32_idb.id0.find(key).value) == '13'


@kern32_test([
    (695, 32, None),
    (700, 32, None),
])
def test_find_exact_match2(kernel32_idb, version, bitness, expected):
    # this is found in the second level, third index
    key = h2b('2e689017765300000009')
    assert kernel32_idb.id0.find(key).key == key
    assert b2h(kernel32_idb.id0.find(key).value) == '02'


@kern32_test([
    (695, 32, '24204636383931344133462e6c705375624b6579'),
    (700, 32, '24204636383931344132452e6c705265736572766564'),
])
def test_find_exact_match3(kernel32_idb, version, bitness, expected):
    # this is found in the root node, last index.
    key = h2b('2eff001bc44e')
    assert kernel32_idb.id0.find(key).key == key
    assert b2h(kernel32_idb.id0.find(key).value) == expected


@kern32_test([
    (695, 32, None),
    (700, 32, None),
])
def test_find_exact_match4(kernel32_idb, version, bitness, expected):
    # this is found on a leaf node, first index
    key = h2b('2e6890142c5300001000')
    assert kernel32_idb.id0.find(key).key == key
    assert b2h(kernel32_idb.id0.find(key).value) == '01080709'


@kern32_test([
    (695, 32, None),
    (700, 32, None),
])
def test_find_exact_match5(kernel32_idb, version, bitness, expected):
    # this is found on a leaf node, fourth index
    key = h2b('2e689a288c530000000a')
    assert kernel32_idb.id0.find(key).key == key
    assert b2h(kernel32_idb.id0.find(key).value) == '02'


@kern32_test([
    (695, 32, None),
    (700, 32, None),
])
def test_find_exact_match6(kernel32_idb, version, bitness, expected):
    # this is found on a leaf node, last index
    key = h2b('2e6890157f5300000009')
    assert kernel32_idb.id0.find(key).key == key
    assert b2h(kernel32_idb.id0.find(key).value) == '02'


@kern32_test()
def test_find_exact_match_min(kernel32_idb, version, bitness, expected):
    minkey = h2b('24204d4158204c494e4b')
    assert kernel32_idb.id0.find(minkey).key == minkey


@kern32_test()
def test_find_exact_match_max(kernel32_idb, version, bitness, expected):
    maxkey = h2b('4e776373737472')
    assert kernel32_idb.id0.find(maxkey).key == maxkey


@kern32_test()
def test_find_exact_match_error(kernel32_idb, version, bitness, expected):
    # check our error handling
    with pytest.raises(KeyError):
        kernel32_idb.id0.find(b'does not exist!')


@kern32_test([(695, 32, None)])
def test_find_prefix(kernel32_idb, version, bitness, expected):
    # nodeid: ff000006 ($fixups)
    fixup_nodeid = '2eff000006'
    key = h2b(fixup_nodeid)

    # the first match is the N (name) tag
    cursor = kernel32_idb.id0.find_prefix(key)
    assert b2h(cursor.key) == fixup_nodeid + h(ord('N'))

    # nodeid: ff000006 ($fixups) tag: S
    supvals = fixup_nodeid + h(ord('S'))
    key = h2b(supvals)

    # the first match is for index 0x68901025
    cursor = kernel32_idb.id0.find_prefix(key)
    assert b2h(cursor.key) == fixup_nodeid + h(ord('S')) + '68901025'

    with pytest.raises(KeyError):
        cursor = kernel32_idb.id0.find_prefix(b'does not exist')


@kern32_test()
def test_find_prefix2(kernel32_idb, version, bitness, expected):
    '''
    this test is derived from some issues encountered while doing import analysis.
    ultimately, we're checking prefix matching when the first match is found
     in a branch node.
    '''
    impnn = idb.netnode.Netnode(kernel32_idb, '$ imports')

    expected_alts = list(range(0x30))
    expected_alts.append(kernel32_idb.uint(-1))
    assert list(impnn.alts()) == expected_alts
    assert list(impnn.sups()) == list(range(0x30))

    # capture the number of supvals in each netnode referenced from the import netnode
    dist = []
    for alt in impnn.alts():
        if alt == kernel32_idb.uint(-1):
            break

        ref = idb.netnode.as_uint(impnn.get_val(alt, tag='A'))
        nn = idb.netnode.Netnode(kernel32_idb, ref)
        dist.append((alt, len(list(nn.sups()))))

    # this distribution was collected empirically.
    # the import analysis is correct (verified in IDA), so by extension, this should be correct as well.
    assert dist == [
        (0, 4), (1, 388), (2, 77), (3, 50), (4, 42), (5, 13), (6, 28), (7, 4),
        (8, 33), (9, 68), (10, 1), (11, 9), (12, 1), (13, 7), (14, 1),
        (15, 24), (16, 9), (17, 6), (18, 26), (19, 9), (20, 54), (21, 24), (22, 8),
        (23, 9), (24, 7), (25, 5), (26, 1), (27, 2), (28, 26), (29, 1),
        (30, 18), (31, 5), (32, 3), (33, 2), (34, 3), (35, 6), (36, 11), (37, 11),
        (38, 5), (39, 6), (40, 11), (41, 7), (42, 10), (43, 14), (44, 38),
        (45, 16), (46, 6), (47, 7)
    ]


@kern32_test([(695, 32, None)])
def test_cursor_easy_leaf(kernel32_idb, version, bitness, expected):
    # this is found on a leaf, second to last index.
    # here's the surrounding layout:
    #
    #      00:00: 2eff00002253689cc95b = ff689cc95b40ff8000c00bd30201
    #    > 00:01: 2eff00002253689cc99b = ff689cc99b32ff8000c00be35101
    #      00:00: 2eff00002253689cc9cd = ff689cc9cd2bff8000c00be12f01
    key = h2b('2eff00002253689cc99b')
    cursor = kernel32_idb.id0.find(key)

    cursor.next()
    assert b2h(cursor.key) == '2eff00002253689cc9cd'

    cursor.prev()
    cursor.prev()
    assert b2h(cursor.key) == '2eff00002253689cc95b'


@kern32_test([(695, 32, None)])
def test_cursor_branch(kernel32_idb, version, bitness, expected):
    # starting at a key that is found in a branch node, test next and prev.
    # these should traverse to leaf nodes and pick the min/max entries, respectively.
    #
    #   576 contents (branch):
    #     ...
    #     000638: 2eff00002253689b9535 = ff689b953573ff441098aa0c040c16000000000000
    #   > 000639: 2eff00002253689bea8e = ff689bea8e8257ff8000c00aa2c601
    #     00000e: 2eff00002253689ccaf1 = ff689ccaf113ff8000c00be25301
    #     ...
    #
    #   638 contents (leaf):
    #     00:00: 2eff00002253689b95db = ff689b95db54ff441098ad08040c14000000000000
    #     00:01: 2eff00002253689b9665 = ff689b96655bff441098b008040815000000000000
    #     00:00: 2eff00002253689b970f = ff689b970f808bff441098b30804141f000000000000
    #     ...
    #     00:01: 2eff00002253689be79b = ff689be79b1bff8000c00a9d4b01
    #     00:00: 2eff00002253689be7b6 = ff689be7b68270ff8000c00af6a101
    #   > 00:00: 2eff00002253689bea26 = ff689bea2668ff8000c00a9f4301
    #
    #
    #   639 contents (leaf):
    #   > 00:00: 2eff00002253689bece5 = ff689bece514ff8000c00bc6b701
    #     00:00: 2eff00002253689becf9 = ff689becf942ff8000c008cf9e01
    #     00:00: 2eff00002253689bed3b = ff689bed3b42ff8000c0090b9c01
    #     ...
    #     00:00: 2eff00002253689cc95b = ff689cc95b40ff8000c00bd30201
    #     00:01: 2eff00002253689cc99b = ff689cc99b32ff8000c00be35101
    #     00:00: 2eff00002253689cc9cd = ff689cc9cd2bff8000c00be12f01

    key = h2b('2eff00002253689bea8e')
    cursor = kernel32_idb.id0.find(key)
    cursor.next()
    assert b2h(cursor.key) == '2eff00002253689bece5'

    key = h2b('2eff00002253689bea8e')
    cursor = kernel32_idb.id0.find(key)
    cursor.prev()
    assert b2h(cursor.key) == '2eff00002253689bea26'


@kern32_test([(695, 32, None)])
def test_cursor_complex_leaf_next(kernel32_idb, version, bitness, expected):
    # see the scenario in `test_cursor_branch`.
    key = h2b('2eff00002253689bea26')
    cursor = kernel32_idb.id0.find(key)
    cursor.next()
    assert b2h(cursor.key) == '2eff00002253689bea8e'


@kern32_test([(695, 32, None)])
def test_cursor_complex_leaf_prev(kernel32_idb, version, bitness, expected):
    # see the scenario in `test_cursor_branch`.
    key = h2b('2eff00002253689bece5')
    cursor = kernel32_idb.id0.find(key)
    cursor.prev()
    assert b2h(cursor.key) == '2eff00002253689bea8e'


@slow
@kern32_test()
def test_cursor_enum_all_asc(kernel32_idb, version, bitness, expected):
    minkey = kernel32_idb.id0.get_min().key
    cursor = kernel32_idb.id0.find(minkey)
    count = 1
    while True:
        try:
            cursor.next()
        except IndexError:
            break
        count += 1

    assert kernel32_idb.id0.record_count == count


@slow
@kern32_test()
def test_cursor_enum_all_desc(kernel32_idb, version, bitness, expected):
    maxkey = kernel32_idb.id0.get_max().key
    cursor = kernel32_idb.id0.find(maxkey)
    count = 1
    while True:
        try:
            cursor.prev()
        except IndexError:
            break
        count += 1

    assert kernel32_idb.id0.record_count == count


@kern32_test([
    (695, 32, None),
    (695, 64, None),
    (700, 32, None),
    (700, 64, None),
])
def test_id1(kernel32_idb, version, bitness, expected):
    id1 = kernel32_idb.id1
    segments = id1.segments

    # collected empirically
    assert len(segments) == 2
    for segment in segments:
        assert segment.bounds.start < segment.bounds.end
    assert segments[0].bounds.start == 0x68901000
    assert segments[1].bounds.start == 0x689DD000

    assert id1.get_segment(0x68901000).bounds.start == 0x68901000
    assert id1.get_segment(0x68901001).bounds.start == 0x68901000
    assert id1.get_segment(0x689dc000 - 1).bounds.start == 0x68901000
    assert id1.get_next_segment(0x68901000).bounds.start == 0x689DD000
    assert id1.get_flags(0x68901000) == 0x2590


def test_id1_2(elf_idb):
    assert list(map(lambda s: s.offset, elf_idb.id1.segments)) == [
        0x0,
        0x8c,
        0x1cec,
        0x47e4c,
        0x7382c,
        0x7385c,
        0x73f9c,
    ]


@kern32_test([
    # collected empirically
    (695, 32, 14252),
    (695, 64, 28504),
    (700, 32, 14247),
    (700, 64, 28494),
])
def test_nam_name_count(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.nam.name_count == expected


@kern32_test([
    # collected empirically
    (695, 32, 8),
    (695, 64, 15),
    (700, 32, 8),
    (700, 64, 15),
])
def test_nam_page_count(kernel32_idb, version, bitness, expected):
    assert kernel32_idb.nam.page_count == expected

    nam = kernel32_idb.nam
    if bitness == 32:
        assert nam.name_count * nam.wordsize < len(nam.buffer)
    elif bitness == 64:
        assert nam.name_count * nam.wordsize > len(nam.buffer)
        assert nam.name_count * nam.wordsize < len(nam.buffer) * 2


@kern32_test([
    # collected empirically
    (695, 32, 14252),
    (695, 64, 14252),
    (700, 32, 14247),
    (700, 64, 14247),
])
def test_nam_names(kernel32_idb, version, bitness, expected):
    names = kernel32_idb.nam.names()
    assert len(names) == expected
    assert names[0] == 0x68901010
    assert names[-1] == 0x689DE228
