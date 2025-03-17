import os
import hashlib
import base64
import asyncio
import aiofiles
import websockchat
import ssl
import dbtalk
import subprocess
import json


CONTENT_TYPES = {
    "html": "text/html",
    "htm": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "json": "application/json",
    "xml": "application/xml",
    "txt": "text/plain",
    "csv": "text/csv",

    # Images
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "webp": "image/webp",
    "svg": "image/svg+xml",

    # Fonts
    "ttf": "font/ttf",
    "otf": "font/otf",
    "woff": "font/woff",
    "woff2": "font/woff2",

    # Audio
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",

    # Video
    "mp4": "video/mp4",
    "webm": "video/webm",
    "ogv": "video/ogg",

    # Archives
    "zip": "application/zip",
    "tar": "application/x-tar",
    "gz": "application/gzip",
    "rar": "application/vnd.rar",
    "7z": "application/x-7z-compressed",

    # PDFs and Documents
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

    # Executables
    "exe": "application/octet-stream",
    "bin": "application/octet-stream",
    "dll": "application/octet-stream",
}

def getContentType(filename):
    return CONTENT_TYPES.get(filename.split('.')[-1],"application/octet-stream")


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
    filename = '.'+req["header"].split()[1]
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
    
    
    if os.path.isdir(filename):
        if filename[-1] != '/':
            return f"""HTTP/1.1 301 Redirect\r\nLocation: {filename}/\r\n\r\n""".encode()
        filename += "index.html"
        

    
    if not args:
        data = await readfile(filename)
        if not data:
            return file_not_found().encode()
        res = f"""HTTP/1.1 200 OK\r\nContent-type: {getContentType(filename)}\r\nContent-length: {len(data)}\r\n\r\n""".encode()+data
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
    if '=' in req["data"]:
        req["data"] = req["data"].split('&')
        datad = {}
        for i in req["data"]:
            key, v = i.split('=')
            datad[key] = v
        req["data"] = datad.copy()
        
        req["data"] =json.dumps(req["data"])
    
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
    
    elif req["header"].startswith("OPTIONS"):
        response = (
            "HTTP/1.1 204 No Content\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            "Access-Control-Allow-Headers: Content-Type\r\n"
            "Content-Length: 0\r\n"
            "Connection: keep-alive\r\n\r\n"
        )
        writer.write(response.encode())
        await writer.drain()
        
        
        


    writer.close()
    await writer.wait_closed()
    

            
        

async def httpReceiver():
    server = await asyncio.start_server(httpHandler,'0.0.0.0', 50)
    print("Listening...")
    async with server:
        await server.serve_forever()
        
                
asyncio.run(httpReceiver())
