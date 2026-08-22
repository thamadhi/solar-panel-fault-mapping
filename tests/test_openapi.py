"""Tests for the OpenAPI / Swagger documentation endpoints."""

import pytest


@pytest.fixture(scope="module")
def client():
    import src.api as api

    api.app.testing = True
    return api.app.test_client()


@pytest.fixture(scope="module")
def spec(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    return resp.get_json()


def test_openapi_spec_is_openapi_3(spec):
    assert spec["openapi"].startswith("3.0")


def test_openapi_spec_has_info(spec):
    assert spec["info"]["title"]
    assert spec["info"]["version"]


def test_documented_paths_match_real_routes(spec, client):
    real_paths = {
        rule.rule for rule in client.application.url_map.iter_rules()
    }
    for path in spec["paths"]:
        # /openapi.json and /docs are the docs themselves; everything else
        # documented must be a real route.
        assert path in real_paths or path in ("/openapi.json", "/docs")


def test_documented_methods_match_real_routes(spec, client):
    real_methods_by_path = {}
    for rule in client.application.url_map.iter_rules():
        methods = {
            m.lower() for m in rule.methods if m not in ("HEAD", "OPTIONS")
        }
        real_methods_by_path[rule.rule] = methods

    for path, operations in spec["paths"].items():
        if path in ("/openapi.json", "/docs"):
            continue
        assert path in real_methods_by_path
        assert set(operations.keys()) == real_methods_by_path[path]


def test_public_endpoints_have_no_security(spec):
    for path in ("/health", "/auth/login"):
        for operation in spec["paths"][path].values():
            assert "security" in operation
            assert operation["security"] == []


def test_protected_endpoints_require_bearer(spec):
    protected = [
        "/predict",
        "/predict-image",
        "/explain/electrical",
        "/localise",
        "/rectify",
        "/assistant/chat",
        "/assistant/history",
    ]
    for path in protected:
        for operation in spec["paths"][path].values():
            assert operation.get("security") == [{"bearerAuth": []}]


def test_bearer_security_scheme_defined(spec):
    scheme = spec["components"]["securitySchemes"]["bearerAuth"]
    assert scheme["type"] == "http"
    assert scheme["scheme"] == "bearer"
    assert scheme["bearerFormat"] == "JWT"


def test_reusable_schemas_are_used(spec):
    refs = []
    for path in spec["paths"].values():
        for operation in path.values():
            for response in operation.get("responses", {}).values():
                content = response.get("content", {})
                for media in content.values():
                    schema = media.get("schema", {})
                    if "$ref" in schema:
                        refs.append(schema["$ref"])
    assert any(ref == "#/components/schemas/Error" for ref in refs)
    assert any(ref.startswith("#/components/schemas/") for ref in refs)


def test_swagger_ui_page_serves_docs(client):
    resp = client.get("/docs")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "swagger-ui" in body
    assert "/openapi.json" in body


def test_no_secrets_in_spec(client):
    text = client.get("/openapi.json").get_data(as_text=True)
    for secret_name in (
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
        "JWT_SECRET",
        "sk-",
    ):
        assert secret_name not in text
