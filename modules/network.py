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
async def get_network_info():
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
