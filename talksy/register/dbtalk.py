import pymongo
from pymongo import MongoClient
import hashlib
import time as tm
from datetime import datetime
import asyncio
import json
from bson.int64 import Int64



client = MongoClient("mongodb://localhost:27017/")
db = client["chatapp"]

nusers = db["nusers"]
users = db["users"]
messages = db["messages"]

def generate_userid():
    c = nusers.find_one()["count"]
    nusers.update_one({},{"$set":{"count": c+1}})
    c = str(c)
    time = datetime.now()
    return f"DRDN{time.year}{len(c)}-{c}"

def generate_token():
    time = datetime.now()
    return str(((time.microsecond * time.hour + (time.second if time.second%2 else time.minute))*97) % 1000000)

async def mail_exists(mail):
    if users.find_one({"email":mail}):
        return True
    return False
    

async def register(args):
    args = json.loads(args)
    if await mail_exists(args["email"]):
        return json.dumps({"status":"failed","type":"email" ,"message":"E-Mail already Exists"})
    if users.find_one({"username":args["username"]}):
        return json.dumps({"status":"failed","type":"username", "message":"Username already Exists"})
    sha_1 = hashlib.sha1()
    sha_1.update(args["password"].encode())
    args["password"] = sha_1.hexdigest()
    args["created_at"] = args["last_online"] = int(tm.time())
    args["userid"] = generate_userid()
    users.insert_one(args)
    return json.dumps({"status":"success"})

async def login(args):
    args = json.loads(args)
    if not users.find_one({"username":args["username"]}):
        return json.dumps({"status":"failed", "type":"Username", "message":"Username Does Not Exists."})
    sha_1 = hashlib.sha1()
    sha_1.update(args["password"].encode())
    passh = sha_1.hexdigest()
    rec = users.find_one({"username":args["username"]})
    if passh != rec["password"]:
        return json.dumps({"status":"failed", "type":"Password", "message":"Invalid Password"})
    token = generate_token()
    users.update_one({"username":args["username"]},{"$set":{"token":token}})
    return json.dumps({"status":"success", "token":token})
        

async def get_profile(username):
    return json.dumps(users.find_one({"username":username},{"_id":0,"password":0}))

async def update_profile(username,args):
    users.update_one({"username":username},{"$set":args})
    return

async def get_token(username):
    return users.find_one({"username":username},{"_id":0,"token":1})

"""------------------------------------------------------------------------------------------------------"""
async def insert_message(msg):
    messages.insert_one(msg)
    return

async def get_unsent(username):
    return messages.find({"receiver":username, "status": 1},{"_id":0}).sort({"time": 1})

async def update_status(msgid, status):
    messages.update_one({"msg_id":msgid},{"$set":{"status":status}})
    return

async def get_conversation(id1, id2 = None, time = None):
    if not time:
        time = int(tm.time()*1000)
    time = Int64(time)
    if not id2:
        return messages.find({"$or":[{"sender":id1},{"receiver":id1}], "time":{"$lt":time}},{"_id":0}).limit(100).sort("time",-1)
    return messages.find({"$or":[{"sender":id1, "receiver":id2},{"sender":id2, "receiver":id1}],"time":{"$lt":time}},{"_id":0}).limit(100).sort("time", -1)






