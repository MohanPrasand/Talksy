import websocket
import collections
import asyncio
import json
import dbtalk


class Users:
    writer:dict = {}
    queue:dict = {}
    token:dict = {}
    online:set = set()
    
    def addUser(userid:str, tkn:str, writer1) -> None:
        Users.writer[userid] = writer1
        Users.queue[userid] = collections.deque()
        Users.token[userid] = tkn
        Users.online.add(userid)
    
    def deleteUser(userid:str) -> None:
        if userid in Users.online:
            del Users.writer[userid]
            del Users.queue[userid]
            del Users.token[userid]
            Users.online.discard(userid)
        
        




async def receive_handler(data: str) -> bool:
    if not data:
        return
    try:
        req:dict = json.loads(data)
        if Users.token[req["sender"]] != req["token"]:
            Users.queue[req["sender"]].appendleft({"type":"logout"})
            asyncio.create_task(req["sender"])
            return
        
        if req["type"] == "message":
            req["status"]=1
            if req["receiver"] in Users.online:
                Users.queue[req["receiver"]].append(req)
                asyncio.create_task(send_handler(req["receiver"]))
            Users.queue[req["sender"]].append({"type":"status", "msg_id":req["msg_id"], "status": 1})
            asyncio.create_task(send_handler(req["sender"]))
            asyncio.create_task(dbtalk.insert_message(req.copy()))
                
        elif req["type"] == "status":
            await dbtalk.update_status(req["msg_id"], req["status"])
            if req["receiver"] in Users.online:
                Users.queue[req["receiver"]].append(req)
                asyncio.create_task(req["receiver"])



    except:
        return False
    return True

sender_set = set()

async def send_handler(id):
    if id in sender_set:
        return
    sender_set.add(id)

    writer = Users.writer[id]
    queue = Users.queue[id]

    while queue:
        msg = queue.popleft()
        try:
            st = await websocket.sender(writer, json.dumps(msg))
            if not st:
                Users.deleteUser(id)

            if msg["type"] == "logout":
                Users.deleteUser(msg["sender"])
                break
            
            if msg["type"] == "message" and msg["status"]<2:
                if msg["sender"] in Users.online:
                    Users.queue[msg["sender"]].append({"type":"status","msg_id": msg["msg_id"], "status":2})
                    asyncio.create_task(send_handler(msg["sender"]))
                asyncio.create_task(dbtalk.update_status(msg["msg_id"],2))
        except Exception as e:
            print(msg)
            print(e)
            
    sender_set.discard(id)



    


async def new_connection(reader, writer):
    try:
        username = None
        data = await websocket.receiver(reader)
        if not data:
            return
        req = json.loads(data)
        if req["type"] != "init":
            return
        username = req["username"]
        token:str = (await dbtalk.get_token(username))["token"]
        if token != req["token"]:
            return
        Users.addUser(username, token, writer)
        older = await dbtalk.get_conversation(username)
        if older:
            for i in older:
                Users.queue[username].append(i)
        asyncio.create_task(send_handler(username))
        await websocket.receiver(reader, receive_handler)
    except Exception as e:
        print(e)        
    finally:
        if username:
            Users.deleteUser(username)
    
        
