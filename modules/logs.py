from main import app
from fastapi import Query

from pydantic import BaseModel
from typing import Optional, Union, List
from enum import Enum
from datetime import datetime

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
        level: Optional[LogLevel] = Query(None, title='Specify loglevel of messages to return'),
        boot: Optional[int] = Query(None, title='Boot number',
                                    description="Specify number of boot which journal will be read"),
        since: Optional[Union[str, int]] = Query(None, description='Return messages since specified date in seconds or '
                                                                   'journalctl supported string format'),
        until: Optional[Union[str, int]] = Query(None, description='Return messages until specified date in seconds or '
                                                                   'journalctl supported string format'),
        day: Optional[str] = Query(None, description='Shorthand property for specifying exact day in ISO format, '
                                                     'e.g. 2022-06-03')):

    args = ['journalctl', '-o', 'json']
    if id:
        args.extend(('-t', id))

    if level:
        args.extend(('-p', str(levels.index(level))))

    if boot is not None:
        args.extend(('-b', str(boot)))

    if day:
        args.extend(('-S', day, '-U', day + ' 23:59:59'))
    else:
        if since:
            if type(since) == str:
                args.extend(('-S', since))
            else:
                args.extend(('-S', datetime.fromtimestamp(since).isoformat(timespec='seconds', sep=' ')))

        if until:
            if type(until) == str:
                args.extend(('-U', until + ' 23:59:59'))
            else:
                args.extend(('-U', datetime.fromtimestamp(until).isoformat(timespec='seconds', sep=' ')))

    print(args)
    output = subprocess.run(args=args, capture_output=True)
    raw_log = json.loads(b'[' + output.stdout.replace(b'\n', b',')[:-1] + b']')

    log = []
    for line in raw_log:
        log.append({'time': float(line['__REALTIME_TIMESTAMP']) / 1000000,
                    'level': levels[int(line['PRIORITY'])],
                    'id': line.get('SYSLOG_IDENTIFIER') if line.get('SYSLOG_IDENTIFIER') else
                    line.get('_COMM') if line.get('_COMM') else line['CODE_FUNC'], 'message': str(line['MESSAGE'])})

    return log
