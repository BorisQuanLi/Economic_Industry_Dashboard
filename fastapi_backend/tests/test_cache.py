"""Tests for Redis cache layer."""

import json
from unittest.mock import MagicMock, patch


def test_cache_get_returns_none_when_redis_unavailable():
    with patch("cache.get_redis", return_value=None):
        from cache import cache_get
        assert cache_get("any_key") is None


def test_cache_get_returns_parsed_json_on_hit():
    mock_redis = MagicMock()
    mock_redis.get.return_value = json.dumps({"sector": "Technology"})
    with patch("cache.get_redis", return_value=mock_redis):
        from cache import cache_get
        result = cache_get("sectors:all:default")
    assert result == {"sector": "Technology"}


def test_cache_get_returns_none_on_miss():
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    with patch("cache.get_redis", return_value=mock_redis):
        from cache import cache_get
        assert cache_get("sectors:all:default") is None


def test_cache_set_calls_setex_with_ttl():
    mock_redis = MagicMock()
    with patch("cache.get_redis", return_value=mock_redis):
        from cache import cache_set, CACHE_TTL
        cache_set("sectors:all:default", {"sector": "Technology"})
    mock_redis.setex.assert_called_once_with(
        "sectors:all:default",
        CACHE_TTL,
        json.dumps({"sector": "Technology"}),
    )


def test_cache_set_is_noop_when_redis_unavailable():
    with patch("cache.get_redis", return_value=None):
        from cache import cache_set
        # Should not raise
        cache_set("key", {"data": 1})
