from main import app
import platform
import threading
from fastapi.responses import JSONResponse

import psutil
from socket import AF_INET, AF_INET6

from pydantic import BaseModel
from common_models import GenericResponseModel

from typing import Dict, Optional
from time import sleep


class NetworkAddrCommonModel(BaseModel):
    address: str
    netmask: str
    broadcast: Optional[str]


class NetworkAddrsModel(BaseModel):
    v4: Optional[NetworkAddrCommonModel]
    v6: Optional[NetworkAddrCommonModel]
    mac: Optional[str]


class NetworkActiveIfaceResponseModel(BaseModel):
    name: str
    type: str


class NetworkMeasureCommonModel(BaseModel):
    recv: int
    sent: int


@app.get('/network/addrs', response_model=Dict[str, NetworkAddrsModel],
         name='Get network interfaces addresses',
         description='Returns an object with interfaces names as keys')
async def get_network_addresses():
    data = psutil.net_if_addrs()
    payload = {}
    for iface in data.items():
        payload[iface[0]] = {}
        for addr in iface[1]:
            addr_type = 'v4' if addr.family == AF_INET else 'v6' if addr.family == AF_INET6 else 'mac'
            payload[iface[0]][addr_type] = addr.address if addr_type == 'mac' else {
                'address': addr.address,
                'netmask': addr.netmask,
                'broadcast': addr.broadcast
            }

    return payload


@app.get('/network/activeIface',
         name='Get current active interface', description='Returns an interface name',
         response_model=NetworkActiveIfaceResponseModel)
async def get_network_active_iface():
    data = psutil.net_if_addrs()
    for iface in data.items():
        ok = False
        for addr in iface[1]:
            if addr.address == '127.0.0.1':
                break
            if addr.family == AF_INET or addr.family == AF_INET6:
                ok = True
                break

        if ok:
            return {'name': iface[0], 'type': 'wifi' if iface[0][0] == 'w' else 'ethernet'}


@app.get('/network/hostname', name="Get the hostname")
async def get_network_hostname():
    return platform.node()

measurer_active = False
oldvals = {}
measure_data = {}


def measurer():
    while True:
        if not measurer_active:
            break
        global measure_data
        global oldvals
        io_counters = psutil.net_io_counters(pernic=True)
        if not oldvals:
            for iface, data in io_counters.items():
                oldvals[iface] = {'recv': data.bytes_recv,
                                  'sent': data.bytes_sent}
                continue

        for iface, data in io_counters.items():
            measure_data[iface] = {'recv': data.bytes_recv - oldvals[iface]['recv'],
                                   'sent': data.bytes_sent - oldvals[iface]['sent']}
            oldvals[iface]['recv'] = data.bytes_recv
            oldvals[iface]['sent'] = data.bytes_sent
        sleep(1)


@app.get('/network/measure/start', name="Start bandwidth measuring thread", response_model=GenericResponseModel,
         responses={400: {'description': 'Returns when measuring thread is already running', 'content': {'text/json': {}}}})
async def start_measuring():
    global measurer_active
    if measurer_active:
        return JSONResponse(status_code=400, content={'status': 'error', 'code': 400,
                                                      'details': 'Measuring thread is already running!'})
    measurer_thread = threading.Thread(target=measurer, name="bandwidth_measurer", daemon=True)
    measurer_active = True
    measurer_thread.start()
    return {'status': 'ok'}


@app.get('/network/measure/stop', name="Stop bandwidth measuring thread", response_model=GenericResponseModel,
         responses={400: {'description': 'Returns when measuring thread is already stopped', 'content': {'text/json': {}}}})
async def stop_measuring():
    global measurer_active, measure_data, oldvals
    if not measurer_active:
        return JSONResponse(status_code=400, content={'status': 'error', 'code': 400,
                                                      'details': 'Measuring thread is already stopped!'})

    measurer_active = False
    measure_data = {}
    oldvals = {}
    return {'status': 'ok'}


@app.get('/network/measure/results', name='Get the results of measure',
         response_model=Dict[str, NetworkMeasureCommonModel],
         responses={400: {'description': 'Returns when measuring thread is dead', 'content': {'text/json': {}}}})
async def get_measure_results():
    if not measurer_active:
        return JSONResponse(status_code=400, content={'status': 'error', 'code': 400,
                                                      'details': 'Measuring thread is dead! No data'})
    return measure_data
