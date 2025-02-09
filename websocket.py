from collections import deque
import asyncio


def write_frame(data):
    data = data.encode()
    n = len(data)
    if n<=125:
        frame = bytes([0x81, n]) + data
    elif n < (1<<16):
        frame = bytes([0x81, 126]) + n.to_bytes(2, 'big') + data
    else:
        frame = bytes([0x81, 127]) + n.to_bytes(8, 'big') + data
    
    return frame
        
def read_frame(data):
    data = bytearray(data)
    ret = {}

    ret["fin"] = data[0]>>7
    ret["opcode"] = data[0]&0b1111

    ret["mask"] = data[1]>>7
    ret["len"] = data[1]&0b1111111

    ind = 2
    if ret["len"]==126:
        ret["len"] = int.from_bytes(data[2:4],'big')
        ind = 4
    elif ret["len"]==127:
        ret["len"] = int.from_bytes(data[2:10],'big')
        ind = 10
    
    if ret["mask"]:
        ret["mask-key"] = bytearray(data[ind:ind+4])
        ind+=4
    
    ret["data"] = ''
    mask = bytearray(ret.get("mask-key",b"\x00\x00\x00\x00"))
    for i in range(ind,ind+ret["len"],4):
        d = bytearray(data[i:i+4])
        dt = bytearray([i^j for i,j in zip(d,mask)])
        if ret["opcode"]==1:
            ret["data"] += dt.decode()
        elif ret["opcode"]==2:
            ret["data"] += dt

    return ret


    

async def sender(writer,msg):
    frame = write_frame(msg)
    writer.write(frame)
    try:
        await asyncio.wait_for(writer.drain(), timeout=2)
    except:
        return False
    return True

    


async def receiver(reader, handler=None):
    data = ''
    while 1:
        rdata = await reader.read(512)
        if not rdata:
            break
        frame = read_frame(rdata)
        data += frame["data"]
        if frame["fin"]:
            if handler:
                asyncio.create_task(handler(data))
                data = ''
            else:
                return data
        
    return 1

