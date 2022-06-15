from main import app
import psutil
import platform
import subprocess

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional


class ErrorMessage(BaseModel):
    message: str


class CPUCountModel(BaseModel):
    count: int
    physical: int


class CPUFreqModel(BaseModel):
    min: int
    max: int
    current: int
    per_cpu: List[int]


class CPULoadPercentModel(BaseModel):
    current: float
    per_cpu: List[float]


class CPUResponseModel(BaseModel):
    name: str
    cpus: CPUCountModel
    freq: CPUFreqModel
    load_percent: CPULoadPercentModel
    load: tuple


class CPUInfoResponseModel(BaseModel):
    name: str
    cpus: CPUCountModel
    arch: str
    vendor_id: Optional[str] = None
    cpu_family: Optional[str] = None
    model: Optional[str] = None
    stepping: Optional[str] = None
    microcode: Optional[str] = None
    flags: Optional[str] = None
    bugs: Optional[str] = None
    features: Optional[str] = None


@app.get('/cpu', response_model=CPUResponseModel)
async def get_cpu_summary():
    freqs = psutil.cpu_freq(True)
    avg_freq = psutil.cpu_freq()
    load_percent = psutil.cpu_percent(interval=0.1, percpu=True)

    temp = 0
    for i in load_percent:
        temp += i
    avg_load_percent = temp / len(load_percent)

    avg_load = psutil.getloadavg()

    return {
        'name': platform.processor(),
        'cpus': {
            'count': psutil.cpu_count(),
            'physical': psutil.cpu_count(False)
        },
        'freq': {
            'min': avg_freq.min,
            'max': avg_freq.max,
            'current': round(avg_freq.current * 1000 if avg_freq.current // 1000 == 0 else avg_freq.current),
            'per_cpu': [round(i.current * 1000) for i in freqs]
        },
        'load_percent': {
            'current': round(avg_load_percent, 1),
            'per_cpu': [i for i in load_percent]
        },
        'load': avg_load,
    }


@app.get('/cpu/info', response_model=CPUInfoResponseModel, responses={501: {
    'description': 'Returns when server is not a Linux machine', 'content': {'text/html': {}}}})
async def get_cpu_info():
    if platform.system() != 'Linux':
        return JSONResponse(status_code=501, content='{"status": "error",'
                                                     '"description": "This feature is for Linux machines only"}')

    output = subprocess.run(['cat', '/proc/cpuinfo'], stdout=subprocess.PIPE, text=True).stdout
    payload = {
        'name': platform.processor(),
        'cpus': {
            'count': psutil.cpu_count(),
            'physical': psutil.cpu_count(False)
        },
        'arch': platform.machine()
    }
    for line in output.split('\n'):
        pos = line.find(':')
        attr = line[:pos].strip().lower()
        if attr == 'vendor_id' or attr == 'cpu family' or attr == 'model' or attr == 'stepping' or attr == 'microcode'\
                or attr == 'flags' or attr == 'bugs' or attr == 'features':
            payload[attr.replace(' ', '_')] = line[pos + 2:]

    return payload
