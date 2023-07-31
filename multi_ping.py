import typer
import subprocess
import asyncio
import time
import re
import time

async def extract_data_from_ping_response(response):
    packets_received = re.search('r"([0-9]+)\s+packets transmitted.*([0-9]+)\s+packets received"', response, re.IGNORECASE)
    return packets_received.group(2)

async def call_subroutine(host):
    response, error = None, None
    print(f'calling subroutine for {host}')
    cmd = ' '.join(['ping', '-c', '1', f'{host}'])
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        response = stdout.decode()
    if stderr:
        error = stderr.decode()
    return response

async def ping(host):
    print(f'pining {host}')
    try:
        response = await call_subroutine(host)
        result = extract_data_from_ping_response(response)
    except subprocess.CalledProcessError:
        result = None
    print(result)
    return result

async def ping_multiple(ips: list[str]):
    print('ping_multiple')
    while True:
        print('cadence loop')
        for p in asyncio.as_completed([ping(ip) for ip in ips]):
            print('ping loop')
            result = await p
        print('cadence loop done, sleeping')
        await asyncio.sleep(1)


def main(ips: list[str]):
    print('main')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ping_multiple(ips))
    loop.close()

# app = typer.Typer()


# @app.command()
# def hello(name: str):
#     print(f"Hello {name}")


# @app.command()
# def goodbye(name: str, formal: bool = False):
#     if formal:
#         print(f"Goodbye Ms. {name}. Have a good day.")
#     else:
#         print(f"Bye {name}!")


if __name__ == "__main__":
    # app(prog_name="mping")
    args = ['1.1.1.1', '8.8.8.8', '192.168.0.1', '1.2.3.4']
    start = time.perf_counter()
    main(args)
    elapsed = time.perf_counter() - start
    print(f"Program completed in {elapsed:0.5f} seconds.")
    