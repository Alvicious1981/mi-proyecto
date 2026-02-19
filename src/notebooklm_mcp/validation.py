from __future__ import annotations

from typing import Any


_TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "array": list,
    "object": dict,
    "boolean": bool,
}


class SchemaValidationError(ValueError):
    """Error de validación de esquema para herramientas MCP."""



def validate_input(arguments: dict[str, Any], schema: dict[str, Any], tool_name: str) -> None:
    if schema.get("type") != "object":
        raise SchemaValidationError(f"Schema inválido para {tool_name}: type debe ser 'object'")

    if not isinstance(arguments, dict):
        raise SchemaValidationError(f"{tool_name}: se esperaba objeto de argumentos")

    required = schema.get("required", [])
    for key in required:
        if key not in arguments:
            raise SchemaValidationError(f"{tool_name}: falta argumento requerido '{key}'")

    properties = schema.get("properties", {})
    for key, value in arguments.items():
        if key not in properties:
            raise SchemaValidationError(f"{tool_name}: argumento no permitido '{key}'")
        _validate_property(value, properties[key], tool_name, key)



def _validate_property(value: Any, prop_schema: dict[str, Any], tool_name: str, key: str) -> None:
    expected_type = prop_schema.get("type")
    if expected_type is None:
        return

    py_type = _TYPE_MAP.get(expected_type)
    if py_type is None:
        raise SchemaValidationError(f"{tool_name}: tipo no soportado en schema para '{key}'")

    if expected_type == "integer" and isinstance(value, bool):
        raise SchemaValidationError(f"{tool_name}: '{key}' debe ser integer")

    if not isinstance(value, py_type):
        raise SchemaValidationError(f"{tool_name}: '{key}' debe ser {expected_type}")

    if expected_type == "array":
        item_schema = prop_schema.get("items")
        if item_schema:
            for idx, item in enumerate(value):
                _validate_property(item, item_schema, tool_name, f"{key}[{idx}]")
        min_items = prop_schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            raise SchemaValidationError(f"{tool_name}: '{key}' requiere al menos {min_items} elementos")

    if expected_type in {"integer", "number"}:
        minimum = prop_schema.get("minimum")
        maximum = prop_schema.get("maximum")
        if minimum is not None and value < minimum:
            raise SchemaValidationError(f"{tool_name}: '{key}' debe ser >= {minimum}")
        if maximum is not None and value > maximum:
            raise SchemaValidationError(f"{tool_name}: '{key}' debe ser <= {maximum}")
