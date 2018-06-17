import os.path
import idb

def test_armel_disasm():
    cd = os.path.dirname(__file__)
    idbpath = os.path.join(cd, 'data', 'armel', 'ls.idb')

    with idb.from_file(idbpath) as db:
        api = idb.IDAPython(db)
        assert api.idc.GetDisasm(0x00002598) == 'push\t{r4, r5, r6, r7, r8, sb, sl, fp, lr}'
        assert api.idc.GetDisasm(0x00012010) == 'b\t#0x12014'

def test_thumb_disasm():
    cd = os.path.dirname(__file__)
    idbpath = os.path.join(cd, 'data', 'thumb', 'ls.idb')

    with idb.from_file(idbpath) as db:
        api = idb.IDAPython(db)
        assert api.idc.GetDisasm(0x00011eac) == 'strb\tr4, [r3, r5]'
        assert api.idc.GetDisasm(0x00011eae) == 'b\t#0x11ebc'

def test_arm64_disasm():
    cd = os.path.dirname(__file__)
    idbpath = os.path.join(cd, 'data', 'arm64', 'ls.i64')

    with idb.from_file(idbpath) as db:
        api = idb.IDAPython(db)
        assert api.idc.GetDisasm(0x00005d30) == 'cmp\tw5, #0x74'
        assert api.idc.GetDisasm(0x00005d34) == 'csel\tw5, w5, w12, ne'
        assert api.idc.GetDisasm(0x00005d38) == 'b\t#0x5c30'


def test_mips_disasm():
    cd = os.path.dirname(__file__)
    idbpath = os.path.join(cd, 'data', 'mips', 'ls.idb')

    with idb.from_file(idbpath) as db:
        api = idb.IDAPython(db)
        assert api.idc.GetDisasm(0x00005440) == 'sb\t$t2, ($t1)'
        assert api.idc.GetDisasm(0x00005444) == 'addiu\t$t3, $t3, 1'
        assert api.idc.GetDisasm(0x00005448) == 'b\t0x523c'

def test_mipsel_disasm():
    cd = os.path.dirname(__file__)
    idbpath = os.path.join(cd, 'data', 'mipsel', 'ls.idb')

    with idb.from_file(idbpath) as db:
        api = idb.IDAPython(db)
        assert api.idc.GetDisasm(0x0000543c) == 'sb\t$t2, ($t1)'
        assert api.idc.GetDisasm(0x00005440) == 'addiu\t$t3, $t3, 1'
        assert api.idc.GetDisasm(0x00005444) == 'b\t0x5238'

def test_mips64el_disasm():
    cd = os.path.dirname(__file__)
    idbpath = os.path.join(cd, 'data', 'mips64el', 'ls.i64')

    with idb.from_file(idbpath) as db:
        api = idb.IDAPython(db)
        assert api.idc.GetDisasm(0x0000b8c8) == 'addiu\t$s0, $s0, -0x57'
        assert api.idc.GetDisasm(0x0000b8cc) == 'daddiu\t$v1, $v1, 1'
        assert api.idc.GetDisasm(0x0000b8d0) == 'b\t0xb760'
