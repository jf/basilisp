import pickle

import pytest

from basilisp.lang import list as llist
from basilisp.lang import map as lmap
from basilisp.lang.interfaces import (
    ILispObject,
    IPersistentCollection,
    IPersistentList,
    IPersistentStack,
    ISeq,
    ISeqable,
    ISequential,
    IWithMeta,
)
from basilisp.lang.keyword import keyword
from basilisp.lang.symbol import symbol


@pytest.mark.parametrize(
    "interface",
    [
        ILispObject,
        IPersistentCollection,
        IPersistentList,
        IPersistentStack,
        ISeq,
        ISeqable,
        ISequential,
        IWithMeta,
    ],
)
def test_list_interface_membership(interface):
    assert isinstance(llist.l(), interface)
    assert issubclass(llist.PersistentList, interface)


def test_list_slice():
    assert isinstance(llist.l(1, 2, 3)[1:], llist.PersistentList)


def test_list_bool():
    assert True is bool(llist.EMPTY)


def test_list_cons():
    meta = lmap.m(tag="async")
    l1 = llist.l(keyword("kw1"), meta=meta)
    l2 = l1.cons(keyword("kw2"))
    assert l1 is not l2
    assert l1 != l2
    assert l2 == llist.l(keyword("kw2"), keyword("kw1"))
    assert len(l2) == 2
    assert meta == l1.meta
    assert l2.meta == meta
    l3 = l2.cons(3, "four")
    assert l3 == llist.l("four", 3, keyword("kw2"), keyword("kw1"))
    assert l3.meta == meta


def test_list_empty():
    meta = lmap.m(tag="async")
    l1 = llist.l(keyword("kw1"), meta=meta)
    assert l1.empty() == llist.EMPTY
    assert l1.empty().meta == meta
    assert llist.EMPTY.empty().meta is None


def test_peek():
    assert None is llist.l().peek()

    assert 1 == llist.l(1).peek()
    assert 1 == llist.l(1, 2).peek()
    assert 1 == llist.l(1, 2, 3).peek()


def test_pop():
    with pytest.raises(IndexError):
        llist.l().pop()

    assert llist.EMPTY == llist.l(1).pop()
    assert llist.l(2) == llist.l(1, 2).pop()
    assert llist.l(2, 3) == llist.l(1, 2, 3).pop()


def test_list_meta():
    assert llist.l("vec").meta is None
    meta = lmap.m(type=symbol("str"))
    assert llist.l("vec", meta=meta).meta == meta


def test_list_with_meta():
    l1 = llist.l("vec")
    assert l1.meta is None

    meta1 = lmap.m(type=symbol("str"))
    l2 = llist.l("vec", meta=meta1)
    assert l2.meta == meta1

    meta2 = lmap.m(tag=keyword("async"))
    l3 = l2.with_meta(meta2)
    assert l2 is not l3
    assert l2 == l3
    assert l3.meta == lmap.m(tag=keyword("async"))

    meta3 = lmap.m(tag=keyword("macro"))
    l4 = l3.with_meta(meta3)
    assert l3 is not l4
    assert l3 == l4
    assert l4.meta == lmap.m(tag=keyword("macro"))


def test_list_seq():
    assert None is llist.EMPTY.seq()
    assert llist.l(1) == llist.l(1).seq()
    assert llist.l(1, 2) == llist.l(1, 2).seq()
    assert llist.l(1, 2, 3) == llist.l(1, 2, 3).seq()


def test_list_first():
    assert None is llist.EMPTY.first
    assert None is llist.l().first
    assert 1 == llist.l(1).first
    assert 1 == llist.l(1, 2).first


def test_list_rest():
    assert llist.l().rest == llist.l()
    assert llist.l(keyword("kw1")).rest == llist.l()
    assert llist.l(keyword("kw1"), keyword("kw2")).rest == llist.l(keyword("kw2"))


@pytest.mark.parametrize(
    "o",
    [
        llist.l(),
        llist.l(keyword("kw1")),
        llist.l(keyword("kw1"), 2),
        llist.l(keyword("kw1"), 2, None, "nothingness"),
        llist.l(keyword("kw1"), llist.l("string", 4)),
    ],
)
def test_list_pickleability(pickle_protocol: int, o: llist.PersistentList):
    assert o == pickle.loads(pickle.dumps(o, protocol=pickle_protocol))


@pytest.mark.parametrize(
    "l,str_repr",
    [
        (llist.l(), "()"),
        (llist.l(keyword("kw1")), "(:kw1)"),
        (llist.l(keyword("kw1"), keyword("kw2")), "(:kw1 :kw2)"),
    ],
)
def test_list_repr(l: llist.PersistentList, str_repr: str):
    assert repr(l) == str_repr
