import typer
import subprocess
import asyncio
import itertools as it
import os
import random
import time


async def ping(host):
    t = time.perf_counter()
    try:
        response = subprocess.check_output(
            ['ping', '-c', '1', f'{host}'],
            universal_newlines=True,
        )
    except subprocess.CalledProcessError:
        response = None
    duration = time.perf_counter() - t
    await asyncio.sleep(1 - duration)
    return response

async def produce(name: int, ip: str, q: asyncio.Queue) -> None:
    while True:
        r = await ping(ip)
        t = time.perf_counter()
        await q.put((r, t))
        print(f"Producer {name} added <{ip}> to queue.")


async def consume(name: int, q: asyncio.Queue) -> None:
    while True:
        ip, t = await q.get()
        now = time.perf_counter()
        print(f"Consumer {name} got element <{ip}>"
              f" in {now-t:0.5f} seconds.")
        q.task_done()


async def main(ips: list[str]):
    q = asyncio.Queue()
    ncon = len(ips)
    consumers = [asyncio.create_task(consume(n, q)) for n in range(ncon)]
    producers = [asyncio.create_task(produce(n, ip, q)) for n, ip in enumerate(ips)]
    await asyncio.gather(*producers)
    await q.join()  # Implicitly awaits consumers, too
    for c in consumers:
        c.cancel()


app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    # app(prog_name="mping")
    args = ['1.1.1.1', '8.8.8.8', '192.168.0.1']
    start = time.perf_counter()
    asyncio.run(main(args))
    elapsed = time.perf_counter() - start
    print(f"Program completed in {elapsed:0.5f} seconds.")
    