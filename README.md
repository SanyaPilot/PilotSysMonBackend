# PilotSysMon Backend

Simple HTTP system monitor API written in Python. Based on FastAPI and psutil.  

## Functions

- Grab OS information
- CPU monitoring (load, frequencies)
- Memory monitoring (RAM / Swap), including additional counters
- Disks information (based on mountpoints)
- Network monitoring, including interfaces' infos and bandwidth measuring

## OS support

In theory, it will run on every platform which is supported by **psutil**, but in practice this API is proved to work on

- Linux (fully works)
- Windows (all works except CPU detailed info and active network interface detection)

> CPU detailed info relies on Linux-only /proc pseudo-FS, so unsupported in other OSes

## Deploying

As FastAPI uses ASGI standard, you can use any ASGI server. I will use **uvicorn** (It is included in requirements.txt file, so if you want to use anything else, just edit it). This guide is written for Linux, but the project is not restricted for it only.

1. **Prepare the environment**  
   First of all, clone the repository:  
   `  git clone https://github.com/SanyaPilot/PilotSysMonBackend`  
   This project fully works in Python **3.9, 3.10**. Other versions are untested, but can work too.  
   It is better to setup Python venv (Virtual ENVironment), but you can use global packages storage. To setup, launch the command below in the project directory:  
   `python -m venv <venv directory>`  
   And activate it using  
   ` source <venv directory>/bin/activate `
2. **Install dependencies**  
   Tell pip to install all packages listed in ` requirements.txt ` in the root of the project's directory:  
   ` pip install -r requirements.txt `
3. **Ready for launch!**  
   All is set up, time to launch ASGI server (using uvicorn as an example)  
   ` uvicorn main:app --host 0.0.0.0 --port 80`  
   You can change bind address and port as you want
4. **Test it out**  
   Navigate to ` <server IP>:<port>/docs` in your browser. Auto-generated docs will appear. Congrats! Now you can start writing your application using this API!