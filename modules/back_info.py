from main import app
import platform
import sys

from pydantic import BaseModel
from typing import Optional

from version import VERSION


class PythonResponse(BaseModel):
    lang: str
    lang_version: str
    version: str
    implementation: str
    venv_path: Optional[str] = None


@app.get('/backend_info', response_model=PythonResponse)
async def get_python_info():
    return PythonResponse(
        lang="python",
        lang_version=platform.python_version(),
        version=VERSION,
        implementation=platform.python_implementation(),
        venv_path=sys.prefix if sys.prefix != sys.base_prefix else None
    )
