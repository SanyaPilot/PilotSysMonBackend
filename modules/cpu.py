from main import app
import psutil
import platform

from pydantic import BaseModel
from typing import List


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


@app.get('/cpu', response_model=CPUResponseModel)
async def get_cpu_info():
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
            'current': round(avg_freq.current * 1000),
            'per_cpu': [round(i.current * 1000) for i in freqs]
        },
        'load_percent': {
            'current': round(avg_load_percent, 1),
            'per_cpu': [i for i in load_percent]
        },
        'load': avg_load,
    }
