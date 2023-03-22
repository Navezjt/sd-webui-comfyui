import asyncio
import os
import sys
import shutil
import subprocess
import multiprocessing
import threading
import time
import socket
import importlib
from lib_comfyui import argv_conversion, webui_settings
importlib.reload(argv_conversion)
importlib.reload(webui_settings)


extension_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
process = None
url_thread = None


def start():
    global process, url_thread
    comfyui_argv = list(sys.argv)
    argv_conversion.set_comfyui_argv(comfyui_argv)
    port = comfyui_argv[comfyui_argv.index('--port') + 1]

    npx_executable = shutil.which('npx')
    if npx_executable is None:
        return

    url_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=on_create_local_tunnel_wrapper, args=(npx_executable, port, url_queue, ), daemon=False)
    sys.path.insert(0, extension_root)
    try:
        process.start()
    finally:
        sys.path.pop(0)

    def update_url():
        while True:
            webui_settings.set_comfyui_url(url_queue.get())

    if url_thread is None:
        url_thread = threading.Thread(target=update_url, daemon=True)
        url_thread.start()


def on_create_local_tunnel_wrapper(npx_executable, port, url_queue):
    npx_process = None
    def on_create_local_tunnel():
        nonlocal npx_process, npx_executable, port, url_queue
        if npx_process is not None:
            return

        wait_for_comfyui_started(int(port))

        print("[ComfyUI] Launching localtunnel...")
        npx_process = subprocess.Popen(
            [npx_executable, 'lt', "--port", port, "--local-host", '127.0.0.1'],
            cwd=extension_root,
            stdout=subprocess.PIPE)
        for line in npx_process.stdout:
            line = line.decode()
            if line.startswith('your url is:'):
                url_queue.put(line.split('your url is:')[1].strip())
            print(f'[ComfyUI] {line}')

    threading.Thread(target=on_create_local_tunnel, daemon=True).start()
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        if npx_process is not None:
            npx_process.kill()
            npx_process = None
    finally:
        loop.close()


# src: https://github.com/comfyanonymous/ComfyUI/blob/master/notebooks/comfyui_colab.ipynb
def wait_for_comfyui_started(port):
    while True:
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            break
        sock.close()


def stop():
    global process
    if process is None:
        return

    process.terminate()
    process = None