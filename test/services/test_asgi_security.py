import pytest
import yaml


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


def test_openapi_documents_api_key_for_protected_routes():
    from app import asgi

    schema = asgi.app.openapi()
    assert schema["components"]["securitySchemes"]["ApiKeyAuth"] == {
        "type": "apiKey",
        "in": "header",
        "name": "x-api-key",
    }
    protected_operations = [
        operation
        for path, methods in schema["paths"].items()
        if path.startswith("/api/v1")
        for operation in methods.values()
        if isinstance(operation, dict) and "responses" in operation
    ]
    assert protected_operations
    assert all(
        {"ApiKeyAuth": []} in operation.get("security", [])
        for operation in protected_operations
    )


def test_release_compose_consumes_hardened_image_and_container_bind():
    with open("docker-compose.release.yml", encoding="utf-8") as compose_file:
        compose = yaml.safe_load(compose_file)

    assert {
        service["image"] for service in compose["services"].values()
    } == {"ghcr.io/dansidanutz/moneyprint:latest"}
    assert compose["services"]["api"]["environment"]["MPT_LISTEN_HOST"] == "0.0.0.0"
    assert compose["services"]["api"]["ports"] == ["127.0.0.1:8080:8080"]
    for readme in ("README.md", "README-en.md"):
        with open(readme, encoding="utf-8") as readme_file:
            documentation = readme_file.read()
        assert "ghcr.io/dansidanutz/moneyprint:latest" in documentation
        assert "ghcr.io/harry0703/moneyprinterturbo:latest" not in documentation
