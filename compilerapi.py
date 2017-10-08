from gevent import monkey; monkey.patch_all()
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask import jsonify
from flask_cors import CORS, cross_origin
import subprocess
import os.path
import urllib, os, uuid
from datetime import datetime
app = Flask(__name__)
CORS(app)
api = Api(app)

class RunC(Resource):
   def post(self):
      parser = reqparse.RequestParser()
      parser.add_argument('code', type=str, required=True, location='json')
      args = parser.parse_args(strict=True)
      code=urllib.unquote(args['code']).decode('utf8') 
      response = []
      unique_filename = str(uuid.uuid4())
      unique_filename = unique_filename[:5]
      with open('/tmp/'+unique_filename+'.c', 'w') as file:
         file.write(code)
      response.append({'file':unique_filename})
      return response, 200

api.add_resource(RunC, '/C/')
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=81)
