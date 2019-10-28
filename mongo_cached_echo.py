#!/usr/bin/env python3
import os
import socket
import redis
import json
import pymongo
from pymongo import MongoClient

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def sendMsg(conn, message):
    conn.sendall(message.encode('utf-8'))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    cache = redis.Redis(host='rediska', port=6379)
    cache.ping()

    client = MongoClient('mongo', 27017)
    db = client.test_database
    kvstorage = db.kvstorage

    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)

            if not data:
                break

            response = {}
            parsed_json = {"action": 0}
            try:
                parsed_json = json.loads(data)
            except ValueError as e:
                response["status"] = "Bad Request"

            action = parsed_json["action"]
            if action == "put":
                res = kvstorage.find_one({"key": parsed_json["key"]})
                if res is not None:
                    kvstorage.find_one_and_delete({"_id": res["_id"]})
                    response["status"] = "Ok"
                else:
                    response["status"] = "Created"

                kvstorage.insert_one({"key": parsed_json["key"], "value": parsed_json["message"]})

            if action == "get":
                if parsed_json.get("no-cache"):
                    res = kvstorage.find_one({"key": parsed_json["key"]})
                    if res is None:
                        response["status"] = "Not found"
                    else:
                        response["status"] = "Ok"
                        response["message"] = res["value"]
                else:
                    key = cache.get(parsed_json["key"])
                    if key is None:
                        db_key = kvstorage.find_one({"key": parsed_json["key"]})
                        if db_key is not None:  # in cache not found but found in db
                            cache.set(parsed_json["key"], db_key["value"]) # Therefore, put it in cache
                            response["status"] = "Ok"
                            response["message"] = db_key["value"]
                        else:
                            response["status"] = "Not found"
                    else:
                        response["status"] = "Ok"
                        if type(key) is bytes:
                            response["message"] = key.decode('utf-8')
                        else:
                            response["message"] = key

            if action == "delete":
                if cache.exists(parsed_json["key"]):
                    cache.delete(parsed_json["key"])
                    response["status"] = "Ok"
                else:
                    response["status"] = "Not found"

            json_string = json.dumps(response)
            sendMsg(conn, json_string + "\n")
