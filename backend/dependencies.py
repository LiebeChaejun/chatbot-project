from typing import Any

app_state: dict[str, Any] = {}

def get_app_state() -> dict[str, Any]:
  return app_state

