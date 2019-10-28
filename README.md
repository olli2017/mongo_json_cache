# mongo_json_cache

**docker-compose build** - собрать  
**docker-compose up** - запустить  

**telnet localhost 2000** - подключиться

Example:  
{"action": "put", "key": 2, "message": "Hello"}  
{"status": "Created"}

{"action": "get", "key": 2, "no-cache":true}   
{"status": "Ok", "message": "Hello"}

{"action": "get", "key": 2}   
{"status": "Ok", "message": "Hello"}

{"action": "put", "key": 2, "message": "Another text"}  
{"status": "Ok"}

взяли свежие из базы  
{"action": "get", "key": 2, "no-cache":true}  
{"status": "Ok", "message": "Another text"}

теперь возьмем из кеша(там еще сохранено старое "Hello")  
{"action": "get", "key": 2}  
{"status": "Ok", "message": "Hello"}

почистим за собой  
{ "action": "delete", "key": 2}  
{"status": "Ok"}

{ "action": "delete", "key": 2}  
{"status": "Not found"}
