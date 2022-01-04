from main import app
import platform
import sys

from pydantic import BaseModel
from typing import Optional


class PythonResponse(BaseModel):
    implementation: str
    version: str
    venv_path: Optional[str] = None


@app.get('/python', response_model=PythonResponse)
async def get_python_info():
    return PythonResponse(implementation=platform.python_implementation(),
                          version=platform.python_version(),
                          venv_path=sys.prefix if sys.prefix != sys.base_prefix else None)
