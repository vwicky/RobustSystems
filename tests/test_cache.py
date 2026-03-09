from src.cache import Cache


def test_cache_add_find_and_clear_roundtrip() -> None:
    cache = Cache(var_id="test_maintainability")

    assert cache.add("foo", {"bar": 1}) is True
    assert cache.find("foo") == {"bar": 1}

    assert cache.clear() is True
    assert cache.find("foo") is None
