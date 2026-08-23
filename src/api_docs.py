"""OpenAPI 3.0 documentation for the PV Insight REST API.

This module keeps a hand-written, dependency-free OpenAPI 3 specification that
mirrors the actual behaviour of the routes defined in :mod:`src.api`. It is
served as JSON at ``/openapi.json`` and rendered with the Swagger UI at
``/docs``.

No secrets are ever embedded in the spec: authentication is documented as a
JWT bearer token, but no example tokens, keys or credentials are included.
"""

from flask import jsonify, render_template_string

# Minimal Swagger UI bootstrap. Assets are loaded from a CDN so no front-end
# build step or vendored files are required.
_SWAGGER_UI_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PV Insight API — Swagger UI</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
window.onload = function () {
    window.ui = SwaggerUIBundle({
        url: {{ spec_url | tojson }},
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis],
        layout: 'BaseLayout',
    });
};
</script>
</body>
</html>
"""


def build_openapi_spec() -> dict:
    """Return the OpenAPI 3.0 specification for the current API.

    Returns:
        dict: The OpenAPI document describing every real endpoint.
    """
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "PV Insight API",
            "description": (
                "REST API for the Solar PV Fault Localisation and Rectification "
                "System. Provides JWT-based authentication, electrical and "
                "thermal fault detection, fault localisation, rectification "
                "recommendations, SHAP explainability and the Solar PV AI "
                "Assistant (chat + history)."
            ),
            "version": "0.1.0",
        },
        "servers": [
            {"url": "/", "description": "Current host (same origin as the client)"},
        ],
        "tags": [
            {"name": "System", "description": "Health and API metadata"},
            {"name": "Authentication", "description": "Login and JWT tokens"},
            {
                "name": "Fault Detection",
                "description": "Electrical and thermal image prediction",
            },
            {"name": "Explainability", "description": "SHAP model explanations"},
            {"name": "Localisation", "description": "Fault string/module localisation"},
            {"name": "Rectification", "description": "Repair recommendations"},
            {
                "name": "AI Assistant",
                "description": "Solar PV AI Assistant chat and history",
            },
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["System"],
                    "summary": "Liveness check",
                    "description": (
                        "Unauthenticated health probe used by container "
                        "orchestrators and load balancers."
                    ),
                    "security": [],
                    "responses": {
                        "200": {
                            "description": "API is alive",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Health"}
                                }
                            },
                        }
                    },
                }
            },
            "/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Authenticate a user",
                    "description": (
                        "Validates the operator credentials and returns a signed "
                        "JWT bearer token plus the user profile."
                    ),
                    "security": [],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LoginResponse"}
                                }
                            },
                        },
                        "400": {
                            "description": "Missing request body",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Invalid credentials",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/auth/register": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "Register a new user account",
                    "description": (
                        "Creates a Standard / Solar PV Operator / Technician "
                        "account (never Admin) and returns a signed JWT bearer "
                        "token so the client is logged in immediately. Body is "
                        "LoginRequest plus 'email' and optional 'user_type'."
                    ),
                    "security": [],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Registration successful",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LoginResponse"}
                                }
                            },
                        },
                        "400": {
                            "description": "Validation error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "409": {
                            "description": "Username or email already taken",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/predict": {
                "post": {
                    "tags": ["Fault Detection"],
                    "summary": "Predict electrical faults",
                    "description": (
                        "Runs the electrical fault detection pipeline on the "
                        "provided inverter readings (a single record or a list of "
                        "records) and persists the prediction."
                    ),
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "oneOf": [
                                        {"$ref": "#/components/schemas/ElectricalReading"},
                                        {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/ElectricalReading"
                                            },
                                        },
                                    ]
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Prediction completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PredictResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "No JSON body provided",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid bearer token",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "500": {
                            "description": "Prediction pipeline failed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/predict-image": {
                "post": {
                    "tags": ["Fault Detection"],
                    "summary": "Detect thermal hotspot faults in an image",
                    "description": (
                        "Uploads a single thermal image as multipart form data "
                        "(field name ``image``) and returns the predicted fault "
                        "type and confidence."
                    ),
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["image"],
                                    "properties": {
                                        "image": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "JPEG/PNG thermal image file.",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Detection completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PredictImageResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Missing image or empty filename",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid bearer token",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "500": {
                            "description": "Detection pipeline failed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/explain/electrical": {
                "post": {
                    "tags": ["Explainability"],
                    "summary": "Explain an electrical prediction with SHAP",
                    "description": (
                        "Computes the SHAP contributions for the selected row of "
                        "an electrical record set and returns the top contributing "
                        "features."
                    ),
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ExplainRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Explanation computed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ExplainResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Invalid body, records or row_idx",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid bearer token",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "500": {
                            "description": "Explanation pipeline failed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/localise": {
                "post": {
                    "tags": ["Localisation"],
                    "summary": "Localise faults from an image or electrical data",
                    "description": (
                        "Two modes are supported:\n\n"
                        "1. **Thermal image** — multipart form data with an "
                        "``image`` file. Returns the predicted fault, confidence, "
                        "location and (when available) a bounding box and an "
                        "annotated image.\n"
                        "2. **Electrical data** — JSON list of inverter reading "
                        "dicts. Returns the predicted fault and the faulty strings.\n\n"
                        "Note: the CSV/Excel ``file`` upload branch is currently "
                        "non-functional in the server and returns an error."
                    ),
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "image": {
                                            "type": "string",
                                            "format": "binary",
                                            "description": "Thermal image file (JPEG/PNG).",
                                        }
                                    },
                                }
                            },
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/ElectricalReading"
                                    },
                                }
                            },
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Localisation completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LocaliseResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Missing/invalid image, body or mode",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid bearer token",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "500": {
                            "description": "Localisation pipeline failed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/rectify": {
                "post": {
                    "tags": ["Rectification"],
                    "summary": "Get rectification recommendations",
                    "description": (
                        "Runs the rectification recommendation pipeline on the "
                        "provided fault data and returns the recommended repair "
                        "actions with cost and downtime estimates."
                    ),
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/RectifyRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Recommendations generated",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RectifyResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "No JSON body provided",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid bearer token",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "500": {
                            "description": "Rectification pipeline failed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/assistant/chat": {
                "post": {
                    "tags": ["AI Assistant"],
                    "summary": "Send a message to the Solar PV AI Assistant",
                    "description": (
                        "Sanitises the operator message, attaches bounded "
                        "application context, asks the configured LLM provider "
                        "(server side only) and persists the exchange per user. "
                        "When no provider is configured the assistant replies "
                        "from its built-in offline knowledge base."
                    ),
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Assistant reply generated",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ChatResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Missing body or empty message",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid bearer token",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                        "500": {
                            "description": "Assistant service failed",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
            "/assistant/history": {
                "get": {
                    "tags": ["AI Assistant"],
                    "summary": "Retrieve the operator's assistant history",
                    "description": (
                        "Returns the signed-in operator's recent assistant "
                        "conversation, oldest first, so the chat widget can "
                        "restore it after a Streamlit rerun."
                    ),
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Conversation history",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ChatHistoryResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Missing or invalid bearer token",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            },
                        },
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": (
                        "JWT returned by POST /auth/login. Send as "
                        "``Authorization: Bearer <token>``."
                    ),
                }
            },
            "schemas": {
                "Health": {
                    "type": "object",
                    "properties": {"status": {"type": "string", "example": "ok"}},
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "error"},
                        "message": {"type": "string"},
                        "error": {"type": "string", "description": "Short error reason."},
                    },
                },
                "LoginRequest": {
                    "type": "object",
                    "required": ["username", "password"],
                    "properties": {
                        "username": {"type": "string", "example": "admin"},
                        "password": {"type": "string", "format": "password"},
                    },
                },
                "UserProfile": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "type": {"type": "string", "example": "Admin"},
                        "username": {"type": "string", "example": "admin"},
                        "email": {"type": "string", "example": "admin@solar.com"},
                    },
                },
                "LoginResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "token": {
                            "type": "string",
                            "description": "Signed JWT bearer token.",
                        },
                        "user": {"$ref": "#/components/schemas/UserProfile"},
                    },
                },
                "ElectricalReading": {
                    "type": "object",
                    "description": (
                        "A single inverter string reading. The exact fields depend "
                        "on the pre-processing pipeline, but commonly include:"
                    ),
                    "properties": {
                        "vdc1": {"type": "number", "example": 600.5},
                        "vdc2": {"type": "number", "example": 598.2},
                        "idc1": {"type": "number", "example": 8.1},
                        "idc2": {"type": "number", "example": 8.0},
                        "irradiance": {"type": "number", "example": 800},
                        "temperature": {"type": "number", "example": 32},
                    },
                },
                "PredictResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "fault_type": {"type": "string", "example": "Open Circuit"},
                        "confidence": {"type": "number", "format": "float", "example": 0.91},
                        "result_readings": {
                            "type": "array",
                            "description": "Processed readings for the UI table.",
                            "items": {"type": "object"},
                        },
                    },
                },
                "PredictImageResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "fault_type": {"type": "string", "example": "Hotspot"},
                        "confidence": {"type": "number", "format": "float", "example": 0.87},
                    },
                },
                "ExplainRequest": {
                    "type": "object",
                    "required": ["records"],
                    "properties": {
                        "records": {
                            "type": "array",
                            "description": "Electrical records to explain.",
                            "items": {
                                "$ref": "#/components/schemas/ElectricalReading"
                            },
                        },
                        "row_idx": {
                            "type": "integer",
                            "default": 0,
                            "description": "Index of the row to explain.",
                            "example": 0,
                        },
                    },
                },
                "FeatureContribution": {
                    "type": "object",
                    "properties": {
                        "feature": {"type": "string"},
                        "value": {"type": "number"},
                        "impact": {"type": "number"},
                        "direction": {
                            "type": "string",
                            "enum": ["pushes forward", "pushes away"],
                        },
                    },
                },
                "ExplainResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "row_idx": {"type": "integer"},
                        "pred_label": {"type": "string"},
                        "confidence": {"type": "number", "format": "float"},
                        "contributors": {
                            "type": "array",
                            "items": {
                                "$ref": "#/components/schemas/FeatureContribution"
                            },
                        },
                    },
                },
                "LocaliseResponse": {
                    "type": "object",
                    "description": (
                        "Shape varies by mode: image requests include "
                        "``bounding_box``/``annotated_image`` when available; "
                        "electrical requests include ``faulty_strings`` and "
                        "``string_reliable``."
                    ),
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "fault_type": {"type": "string", "example": "Hotspot"},
                        "confidence": {"type": "number", "format": "float", "example": 0.82},
                        "location": {"type": "string", "example": "String 3, Module 7"},
                        "bounding_box": {
                            "type": "array",
                            "description": "Optional image bounding box.",
                            "items": {"type": "number"},
                        },
                        "annotated_image": {
                            "type": "string",
                            "format": "byte",
                            "description": "Optional base64-encoded annotated image.",
                        },
                        "faulty_strings": {
                            "type": "array",
                            "description": "Optional per-string results.",
                            "items": {"type": "object"},
                        },
                        "string_reliable": {
                            "type": "boolean",
                            "description": "Whether string localisation is reliable.",
                        },
                    },
                },
                "RectifyRequest": {
                    "type": "object",
                    "description": "Fault data used to derive recommendations.",
                    "properties": {
                        "fault_type": {"type": "string"},
                        "severity": {"type": "string"},
                        "location": {"type": "string"},
                    },
                },
                "RectifyResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "fault_type": {"type": "string"},
                        "location": {"type": "string"},
                        "severity": {"type": "string"},
                        "confidence": {"type": "number", "format": "float"},
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "best_action": {"type": "string"},
                        "best_cost": {"type": "number"},
                        "best_downtime": {"type": "string"},
                    },
                },
                "ChatRequest": {
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The operator's message to the assistant.",
                            "example": "What faults were detected?",
                        },
                        "page": {
                            "type": "string",
                            "description": "Current page name for context.",
                            "example": "Fault Detection",
                        },
                        "page_data": {
                            "type": "object",
                            "description": "Optional compact frontend context.",
                        },
                    },
                },
                "ChatResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "reply": {"type": "string", "description": "Assistant reply."},
                        "provider_configured": {
                            "type": "boolean",
                            "description": "False when no LLM provider is configured.",
                        },
                        "error": {
                            "type": ["string", "null"],
                            "description": "Provider error, if any.",
                        },
                        "provider": {
                            "type": ["string", "null"],
                            "description": "Provider name, if any.",
                        },
                    },
                },
                "ChatHistoryResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "messages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {
                                        "type": "string",
                                        "enum": ["user", "assistant"],
                                    },
                                    "content": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        },
    }


def register_docs(app) -> None:
    """Register the OpenAPI JSON and Swagger UI routes on ``app``."""

    @app.get("/openapi.json")
    def openapi_json():
        return jsonify(build_openapi_spec())

    @app.get("/docs")
    def docs():
        return render_template_string(
            _SWAGGER_UI_TEMPLATE,
            spec_url="/openapi.json",
        )
