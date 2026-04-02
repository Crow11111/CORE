"""
CORE-GENESIS: Tool Registry
VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
"""

import inspect
from typing import Any, Callable, Dict, List, get_type_hints

class ToolRegistry:
    """
    Registriert Python-Funktionen als LLM-kompatible JSON-Schemas
    (für Gemini/Claude Tools) und führt sie deterministisch aus.
    """

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def _type_to_json_schema(self, py_type: Any) -> str:
        """Übersetzt Python-Typen in JSON-Schema-Typen."""
        if py_type == str:
            return "string"
        elif py_type == int:
            return "integer"
        elif py_type == float:
            return "number"
        elif py_type == bool:
            return "boolean"
        elif py_type == list or py_type == List:
            return "array"
        elif py_type == dict or py_type == Dict:
            return "object"
        return "string"

    def register(self, func: Callable, name: str = None, description: str = None) -> None:
        """
        Registriert eine Funktion als Tool und generiert das JSON-Schema.
        """
        func_name = name or func.__name__
        func_desc = description or inspect.getdoc(func) or "Keine Beschreibung verfügbar."

        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Überspringe self in Klassenmethoden (falls als ungebundene Methode registriert wird)
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name, str)
            properties[param_name] = {
                "type": self._type_to_json_schema(param_type),
                "description": f"Parameter {param_name}"
            }
            if param.default == inspect.Parameter.empty:
                required = required + [param_name]

        # Nimm die erste Zeile der Beschreibung für das Schema, wenn sie existiert
        desc_lines = func_desc.strip().split('\n')
        short_desc = desc_lines[0] if desc_lines else "Keine Beschreibung verfügbar."

        schema = {
            "name": func_name,
            "description": short_desc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

        self._tools[func_name] = func
        self._schemas = self._schemas + [schema]

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Gibt die JSON-Schemas aller registrierten Tools zurück."""
        return self._schemas

    async def execute(self, name: str, **kwargs) -> Any:
        """
        Führt ein registriertes Tool aus.
        Wenn das Tool async ist, wird es awaited.
        """
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' ist nicht registriert.")

        func = self._tools[name]

        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)
