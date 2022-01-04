from main import app
import platform

from pydantic import BaseModel
from typing import Optional


class OSResponseModel(BaseModel):
    family: str
    name: Optional[str] = None
    version: Optional[str] = None
    release: str
    build: Optional[str] = None
    edition: Optional[str] = None
    url: Optional[str] = None


@app.get("/os", response_model=OSResponseModel)
async def get_os_info():
    family = platform.system()
    if family == 'Linux':
        freedesktop_info = platform.freedesktop_os_release()
        response = {'family': family, 'name': freedesktop_info['NAME'], 'version': freedesktop_info.get('VERSION_ID'),
                    'release': platform.release(), 'url': freedesktop_info.get('HOME_URL')}
    elif family == 'Windows':
        win_info = platform.win32_ver()
        response = {'family': family, 'release': win_info[0], 'build': win_info[1], 'edition': platform.win32_edition()}
    elif family == 'Darwin':
        response = {'family': 'macOS', 'version': platform.mac_ver()[0], 'release': platform.release()}
    else:
        response = {'family': family, 'version': platform.version(), 'release': platform.release()}

    return response
