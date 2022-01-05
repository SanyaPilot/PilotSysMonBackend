from main import app
from fastapi import Query

import psutil
from psutil._common import bytes2human

from pydantic import BaseModel
from typing import List, Union, Optional


class DiskUsageModel(BaseModel):
    total: Union[int, str]
    used: Union[int, str]
    free: Union[int, str]
    percent: float


class DisksResponseModel(BaseModel):
    device: str
    mountpoint: str
    fs: str
    opts: str
    usage: DiskUsageModel


@app.get('/disks', response_model=List[DisksResponseModel])
async def get_disks_info(human: Optional[bool] = Query(
        False, title='Human-readable', description='If set to true, values are sent as strings with unit postfix')):
    payload = []
    for disk in psutil.disk_partitions():
        usage = psutil.disk_usage(disk.mountpoint)
        temp = {
            'device': disk.device,
            'mountpoint': disk.mountpoint,
            'fs': disk.fstype,
            'opts': disk.opts,
            'usage': {}
        }
        for key in usage._fields:
            attr = getattr(usage, key)
            temp['usage'][key] = bytes2human(attr) if key != 'percent' and human else attr
        payload.append(temp)

    return payload
