import pytest

from cfmtoolbox.dict_cache import DictCache


def test_add_and_contains():
    cache = DictCache(max_size=3)
    item = {"key": "value"}
    cache.add(item)
    assert cache.contains(lambda d: d["key"] == "value") is True


def test_add_non_dict_raises():
    cache = DictCache()
    with pytest.raises(ValueError, match="Only dictionaries can be stored"):
        cache.add(["not", "a", "dict"])


def test_eviction_policy():
    cache = DictCache(max_size=2)
    cache.add({"a": 1})
    cache.add({"b": 2})
    cache.add({"c": 3})
    assert not cache.contains(lambda d: "a" in d)
    assert cache.contains(lambda d: "b" in d)
    assert cache.contains(lambda d: "c" in d)


def test_find_returns_correct_dict():
    cache = DictCache()
    d1 = {"id": 1}
    d2 = {"id": 2}
    cache.add(d1)
    cache.add(d2)
    found = cache.find(lambda d: d["id"] == 2)
    assert found == d2


def test_find_returns_none_if_not_found():
    cache = DictCache()
    cache.add({"a": 10})
    result = cache.find(lambda d: d.get("b") == 20)
    assert result is None


def test_remove_entry():
    cache = DictCache()
    d = {"to_remove": True}
    cache.add(d)
    cache.remove(d)
    assert not cache.contains(lambda entry: "to_remove" in entry)


def test_clear_cache():
    cache = DictCache()
    cache.add({"a": 1})
    cache.clear()
    assert len(list(cache)) == 0


def test_cache_is_iterable():
    cache = DictCache()
    items = [{"a": 1}, {"b": 2}]
    for item in items:
        cache.add(item)
    assert list(cache) == items
