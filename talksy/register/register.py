import sys
import dbtalk
import asyncio

args = sys.argv[1]

async def reg():
    status = await dbtalk.register(args)
    print(status)

asyncio.run(reg())
    

