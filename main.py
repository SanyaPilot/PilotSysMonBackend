from enum import Enum
import platform
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration. Edit if necessary
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/os")
async def get_os_info():
    family = platform.system()
    if family == 'Linux':
        freedesktop_info = platform.freedesktop_os_release()
        response = {'family': family, 'name': freedesktop_info['NAME'], 'version': freedesktop_info.get('VERSION_ID'),
                    'kernel': platform.release(), 'url': freedesktop_info.get('HOME_URL')}
    elif family == 'Windows':
        win_info = platform.win32_ver()
        response = {'family': family, 'release': win_info[0], 'build': win_info[1], 'edition': platform.win32_edition()}
    elif family == 'Darwin':
        response = {'family': 'macOS', 'release': platform.mac_ver()[0], 'kernel': platform.release()}
    else:
        response = {'family': family, 'version': platform.version(), 'release': platform.release()}

    return response
