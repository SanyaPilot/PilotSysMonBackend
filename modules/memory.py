from main import app
import psutil
from psutil._common import bytes2human

from pydantic import BaseModel


class MemoryCommonModel(BaseModel):
    percent: float
    raw: dict
    human: dict


class MemoryResponseModel(BaseModel):
    ram: MemoryCommonModel
    swap: MemoryCommonModel


@app.get('/memory', response_model=MemoryResponseModel)
async def get_memory_info():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    payload = {
        'ram': {
            'percent': memory.percent,
            'raw': {},
            'human': {}
        },
        'swap': {
            'percent': swap.percent,
            'raw': {},
            'human': {}
        }
    }
    for key in payload.keys():
        for key2 in payload[key].keys():
            if key2 == 'percent':
                continue
            obj = memory if key == 'ram' else swap
            for key3 in obj._fields:
                if key3 == 'percent':
                    continue
                value = getattr(obj, key3)
                payload[key][key2][key3] = value if key2 == 'raw' else bytes2human(value)
    return payload
