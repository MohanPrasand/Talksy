import sys
import dbtalk
import asyncio

async def log():
    args = sys.argv[1]

    status = await dbtalk.login(args)

    print(status)

asyncio.run(log())

