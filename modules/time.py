from main import app
import psutil
import time

from pydantic import BaseModel


class TimeResponseModel(BaseModel):
    time: int
    timezone: str
    uptime: int


@app.get('/time', name='Get server time information', response_model=TimeResponseModel)
async def get_time_info():
    return {
        'time': time.time() + time.timezone * -1,
        'timezone': time.tzname[0],
        'uptime': time.time() - psutil.boot_time()
    }
