from main import app
from fastapi import Query

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

import subprocess
import json

levels = ['emerg', 'alert', 'crit', 'error', 'warn', 'notice', 'info', 'debug']


class LogLevel(str, Enum):
    EMERG = 'emerg'
    ALERT = 'alert'
    CRIT = 'crit'
    ERROR = 'error'
    WARN = 'warn'
    NOTICE = 'notice'
    INFO = 'info'
    DEBUG = 'debug'


class LogEntryModel(BaseModel):
    time: float
    level: str
    id: str
    message: str


@app.get('/logs', response_model=List[LogEntryModel])
async def get_logs(id: Optional[str] = Query(
        None, title='Syslog identifier', description='Specify syslog ID of messages to return'),
        level: Optional[LogLevel] = Query(None, title='Specify loglevel of messages to return')):

    args = ['journalctl', '-b', '-o', 'json']
    if id:
        args.extend(('-t', id))

    if level:
        args.extend(('-p', str(levels.index(level))))

    print(args)
    output = subprocess.run(args=args, capture_output=True)
    raw_log = json.loads(b'[' + output.stdout.replace(b'\n', b',')[:-1] + b']')

    log = []
    for line in raw_log:
        log.append({'time': float(line['__REALTIME_TIMESTAMP']) / 1000000,
                    'level': levels[int(line['PRIORITY'])],
                    'id': line.get('SYSLOG_IDENTIFIER') if line.get('SYSLOG_IDENTIFIER') else line['_COMM'], 'message': str(line['MESSAGE'])})

    return log
