from main import app
import platform

import psutil
from socket import AF_INET, AF_INET6

from pydantic import BaseModel
from typing import Dict, Optional


class NetworkAddrCommonModel(BaseModel):
    address: str
    netmask: str
    broadcast: Optional[str]


class NetworkAddrsModel(BaseModel):
    v4: Optional[NetworkAddrCommonModel]
    v6: Optional[NetworkAddrCommonModel]
    mac: str


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
         name='Get current active interface', description='Returns an interface name')
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
