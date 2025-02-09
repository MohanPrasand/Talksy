import os
import hashlib
import base64
import asyncio
import aiofiles
import websockchat
import subprocess
import json


async def readfile(fname: str) -> bytes:
    fname = './'+fname[1:]

    if not fname or os.path.isdir(fname):
        fname += "/index.html"

    if not os.path.isfile(fname):
        return None
    data = ''
    async with aiofiles.open(fname,mode="rb") as file:
        return await file.read()

def formatRequest(request):
    req = {"data":""}
    request = request.split("\r\n")
    req["header"] = request[0]
    isData = False
    for line in request[1:]:
        if isData:
            req["data"]+=line
        elif not line:
            isData = True
        elif ":" in line:
            t,q = line.split(":",1)
            req[t] = q.strip()
    
    return req

def calcAccKey(key):
    combined = key+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    sha1H = hashlib.sha1(combined.encode()).digest()
    sec_ws = base64.b64encode(sha1H).decode()
    return sec_ws

def file_not_found():
    data = "<html><h1>File Not Found</h1></html>"
    res = ("HTTP/1.1 404 NotFound\r\n"
            "Content-type: text\html\r\n"
            f"Content-length: {len(data)}\r\n\r\n"
            f"{data}")
    return res

async def handle_get(req):
    filename = req["header"].split()[1]
    if '?'in filename:
        filename, args = filename.split('?')
        args = args.split('&')
        argd={}
        for i in args:
            i,j = i.split('=')
            argd[i]=j
        args = json.dumps(argd)
        
    else:
        args = None
    
    
    if os.path.isdir('.'+filename) and filename[-1] != '/':
        return f"""HTTP/1.1 301 Redirect\r\nLocation: {filename}/\r\n\r\n""".encode()
        

    
    if not args:
        data = await readfile(filename)
        if not data:
            return file_not_found().encode()
        res = f"""HTTP/1.1 200 OK\r\nContent-type: text\html\r\nContent-length: {len(data)}\r\n\r\n""".encode()+data
        return res
    
    command = "php" if filename.endswith("php") else "python"
    
    if command == "php":
        env = os.environ.copy()
        env["METHOD"] = "GET"
        env["QUERY_STRING"] = args
        process = subprocess.Popen(
            [command, filename],
            stdout= subprocess.PIPE,
            stderr= subprocess.PIPE,
            env= env,
            text= True
        )
    elif command=="python":
        process = subprocess.Popen(
            [command, filename] + [args,],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            text = True
        )
    output, error = process.communicate()
    if error:
        res = f"""HTTP/1.1 400 Bad Request\r\nContent-type: text/html\r\nContent-length: {len(error)}\r\n\r\n"""+error
    else:        
        res = f"""HTTP/1.1 200 OK\r\nContent-type: text/html\r\nContent-length: {len(output)}\r\n\r\n"""+output
    
    return res.encode()

async def handle_post(req):
    filename = req["header"].split()[1]
    filename = '.' + filename
    if not os.path.isfile(filename):
        data = "<html><h1>File Not Found</h1></html>"
        res = ("HTTP/1.1 404 NotFound\r\n"
                "Content-type: text\html\r\n"
                f"Content-length: {len(data)}\r\n\r\n"
                f"{data}").encode()
        return res
    data = req["data"].split('&')
    datad = {}
    for i in data:
        key, val = i.split('=')
        datad[key] = val
    
    req["data"] =json.dumps(datad)
    prcs = subprocess.Popen(["python",filename]+[req["data"],],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text= True)
    
    output, error = prcs.communicate()
    if error:
        res = f"""HTTP/1.1 400 Bad Request\r\nContent-type: text/html\r\nContent-length: {len(error)}\r\n\r\n"""+error
    else:        
        res = f"""HTTP/1.1 200 OK\r\nContent-type: text/html\r\nContent-length: {len(output)}\r\n\r\n"""+output
    
    return res.encode()



async def httpHandler(reader, writer):
    request = await reader.read(1024)
    req = formatRequest(request.decode())
    
    if "Connection" in req and req["Connection"]=="Upgrade" and req["Upgrade"]=="websocket":
        accKey = calcAccKey(req["Sec-WebSocket-Key"])
        res = f"HTTP/1.1 101 Switching Protocols\r\nConnection: upgrade\r\nUpgrade: websocket\r\nSec-Websocket-Accept: {accKey}\r\n\r\n".encode()
        writer.write(res)
        await writer.drain()
        asyncio.create_task(websockchat.new_connection(reader,writer))
        return
        
    elif req["header"].startswith("GET"):
        writer.write(await handle_get(req))
        await writer.drain()

    elif req["header"].startswith("POST"):
        writer.write(await handle_post(req))
        await writer.drain()
        
        


    writer.close()
    await writer.wait_closed()
    

            
        

async def httpReceiver():
    server = await asyncio.start_server(httpHandler,'0.0.0.0', 50)
    print("Listening...")
    async with server:
        await server.serve_forever()
        
                
asyncio.run(httpReceiver())