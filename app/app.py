import os
import sys
from flask import Flask,request,jsonify
import functools
import json
import logging
from pymemcache.client.base import Client
#сериализатор
def json_serializer(key, value):
    if type(value) == str:
        return value, 1
    return json.dumps(value), 2
#десериализатор
def json_deserializer(key, value, flags):
   if flags == 1:
       return value.decode("utf-8")
   if flags == 2:
       return json.loads(value.decode("utf-8"))
   raise Exception("Unknown serialization format")

MEMCACHE_HOST = os.environ.get("MEMCACHE_HOST")
MEMCACHE_PORT = int(os.environ.get("MEMCACHE_PORT", 11211))
client = Client((MEMCACHE_HOST , MEMCACHE_PORT), serializer=json_serializer,
                deserializer=json_deserializer)
#client.set('key', {'a':'b', 'c':'d'})
#result = client.get('key')
#print(result)


#функция расчета чисел фибоначи
@functools.lru_cache(maxsize=128, typed=False)
def fibo_steroids(n):
    if n in [0, 1]:
        return n
    else:
        return fibo_steroids(n-1) + fibo_steroids(n-2)
sys.setrecursionlimit(30000)

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))
@app.route('/')
def hello_world():
    return 'Программа расчета чисел Фибоначи'

@app.route("/<number>", methods=['GET'])
def get_fibonacci_api(number):
    number = int(number)
    result = client.get('{}'.format(number))
    if result:
       logging.info("For %s stored value is used" % number)
       return jsonify(number=result)
    f_number = fibo_steroids(number)
    logging.info("For %s new value is calculated" % number)
    client.set('{}'.format(number),'{}'.format(f_number))
    return jsonify(number=f_number)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)
