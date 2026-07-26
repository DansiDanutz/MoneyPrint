import pytest


def test_cors_defaults_to_explicit_local_origins(monkeypatch):
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    from app import asgi

    assert asgi.get_cors_origins() == [
        "http://127.0.0.1:8501",
        "http://localhost:8501",
    ]


def test_cors_rejects_wildcard_with_credentials(monkeypatch):
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")
    from app import asgi

    with pytest.raises(RuntimeError, match="explicit origins"):
        asgi.get_cors_origins()
