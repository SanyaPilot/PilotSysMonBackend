from main import app
import psutil
import platform


@app.get('/cpu')
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
