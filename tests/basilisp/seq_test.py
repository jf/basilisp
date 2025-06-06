import pytest

from basilisp.lang import keyword as kw
from basilisp.lang import list as llist
from basilisp.lang import runtime as runtime
from basilisp.lang import seq as lseq
from basilisp.lang import vector as vec


def test_to_sequence():
    assert lseq.EMPTY == lseq.sequence([])
    assert lseq.sequence([]).is_empty
    assert llist.l(None) == lseq.sequence([None])
    assert not lseq.sequence([None]).is_empty
    assert llist.l(1) == lseq.sequence([1])
    assert not lseq.sequence([1]).is_empty
    assert llist.l(1, 2, 3) == lseq.sequence([1, 2, 3])
    assert not lseq.sequence([1, 2, 3]).is_empty


def test_lazy_sequence():
    s = lseq.LazySeq(lambda: None)
    assert s.is_empty
    assert None is s.first
    assert lseq.EMPTY is s.rest
    assert s.is_realized
    assert s.is_empty, "LazySeq has been realized and is empty"

    s = lseq.LazySeq(lambda: lseq.EMPTY)
    assert s.is_empty
    assert None is s.first
    assert lseq.EMPTY is s.rest
    assert s.is_realized
    assert s.is_empty, "LazySeq has been realized and is empty"

    s = lseq.LazySeq(lambda: lseq.sequence([1]))
    assert not s.is_empty
    assert 1 == s.first
    assert lseq.EMPTY == s.rest
    assert s.rest.is_empty
    assert s.is_realized
    assert not s.is_empty, "LazySeq has been realized and is not empty"

    def lazy_seq():
        def inner_seq():
            def inner_inner_seq():
                return lseq.sequence([3])

            return lseq.LazySeq(inner_inner_seq).cons(2)

        return lseq.LazySeq(inner_seq).cons(1)

    s = lseq.LazySeq(lazy_seq)
    assert not s.is_empty
    assert 1 == s.first
    assert isinstance(s.rest, lseq.LazySeq)
    assert s.is_realized
    assert not s.is_empty, "LazySeq has been realized and is not empty"

    r = s.rest
    assert not r.is_empty
    assert 2 == r.first
    assert isinstance(r.rest, lseq.LazySeq)
    assert r.is_realized
    assert not r.is_empty, "LazySeq has been realized and is not empty"

    t = r.rest
    assert not t.is_empty
    assert 3 == t.first
    assert lseq.EMPTY == t.rest
    assert t.rest.is_empty
    assert t.is_realized
    assert not t.is_empty, "LazySeq has been realized and is not empty"

    assert [1, 2, 3] == [e for e in s]

    def raise_error(er):
        raise er

    s = lseq.LazySeq(lambda: raise_error(BaseException))
    with pytest.raises(BaseException):
        s.first
    s = lseq.LazySeq(lambda: raise_error(AttributeError))
    with pytest.raises(AttributeError):
        s.first


def test_empty_sequence():
    empty = lseq.sequence([])
    assert empty.is_empty
    assert None is empty.first
    assert empty.rest == empty
    assert llist.l(1) == empty.cons(1)
    assert lseq.EMPTY == empty
    assert empty.is_empty
    assert True is bool(lseq.sequence([]))


def test_sequence():
    s = lseq.sequence([1])
    assert not s.is_empty
    assert 1 == s.first
    assert lseq.EMPTY == s.rest
    assert s.rest.is_empty
    assert llist.l(2, 1) == s.cons(2)
    assert [1, 2, 3] == [e for e in lseq.sequence([1, 2, 3])]
    assert llist.l(1, 2, 3) == lseq.sequence([1, 2, 3])
    assert llist.l(1, 2, 3) == lseq.sequence(llist.l(1, 2, 3))
    assert llist.l(1, 2, 3) == llist.list(lseq.sequence([1, 2, 3]))

    s = lseq.sequence([1, 2, 3])
    assert not s.is_empty
    assert 2 == s.rest.first
    assert 3 == s.rest.rest.first
    assert None is s.rest.rest.rest.first


def test_seq_iterator():
    s = lseq.sequence([])
    assert vec.EMPTY == vec.vector(s)

    s = lseq.sequence(range(10000))
    assert 10000 == len(vec.vector(s))


def test_seq_iterables():
    iterable1 = range(3)
    s1 = lseq.sequence(iterable1)
    s2 = lseq.sequence(iterable1)
    assert 3 == runtime.count(s1)
    assert llist.l(0, 1, 2) == s1 == s2

    # A generator is an example of a single-use iterable
    iterable2 = (i for i in [4, 5, 6])
    with pytest.raises(TypeError):
        lseq.sequence(iterable2)
    with pytest.raises(TypeError):
        runtime.count(iterable2)

    s3 = lseq.iterator_sequence(iterable2)
    assert 3 == runtime.count(s3)
    assert llist.l(4, 5, 6) == s3


def test_seq_equals():
    # to_seq should be first to ensure that `ISeq.__eq__` is used
    assert runtime.to_seq(vec.v(1, 2, 3)) == llist.l(1, 2, 3)
    assert False is (runtime.to_seq(vec.v(1, 2, 3)) == kw.keyword("abc"))

    assert lseq.sequence(vec.v(1, 2, 3)) == llist.l(1, 2, 3)
    assert False is (lseq.sequence(vec.v(1, 2, 3)) == kw.keyword("abc"))
