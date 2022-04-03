from main import app
from fastapi import Query

import psutil
from psutil._common import bytes2human

from pydantic import BaseModel
from typing import Optional, Union


class RAMModel(BaseModel):
    percent: float
    total: Union[int, str]
    available: Union[int, str]
    used: Union[int, str]
    free: Union[int, str]
    active: Optional[Union[int, str]] = None
    inactive: Optional[Union[int, str]] = None
    buffers: Optional[Union[int, str]] = None
    cached: Optional[Union[int, str]] = None
    shared: Optional[Union[int, str]] = None
    slab: Optional[Union[int, str]] = None
    wired: Optional[Union[int, str]] = None


class SwapModel(BaseModel):
    percent: float
    total: Union[int, str]
    used: Union[int, str]
    free: Union[int, str]
    sin: Union[int, str]
    sout: Union[int, str]


class MemoryResponseModel(BaseModel):
    ram: RAMModel
    swap: Optional[SwapModel] = None


@app.get('/memory', response_model=MemoryResponseModel)
async def get_memory_info(human: Optional[bool] = Query(
        False, title='Human-readable', description='If set to true, values are sent as strings with unit postfix')):
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    payload = {
        'ram': {},
        'swap': None if swap.total == 0 else {}
    }
    for key in payload.keys():
        obj = memory if key == 'ram' else swap
        if obj.total == 0:
            break
        for key2 in obj._fields:
            value = getattr(obj, key2)
            payload[key][key2] = bytes2human(value) if key2 != 'percent' and human else value
    return payload
