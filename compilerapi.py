from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask import jsonify
import subprocess
import urllib
app = Flask(__name__)
api = Api(app)

class RunC(Resource):
   def post(self):
      parser = reqparse.RequestParser()
      parser.add_argument('code', type=str, required=True, location='json')
      args = parser.parse_args(strict=True)
      code=urllib.unquote(args['code']).decode('utf8') 
      print code
      response = []
      with open('test.c', 'w') as file:
         file.write(code)
      p = subprocess.Popen(['gcc', 'test.c', '-o', 'test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      out, err = p.communicate()
      if (err):
          print "Error"
          response.append({'success':'false','error':err})
          return jsonify(result = response)
      print "Success"
      q = subprocess.check_output(['./test'])
      response.append({'success':'true','output':q})
      return jsonify(result = response)
      
      
        
api.add_resource(RunC, '/C/')

if __name__ == '__main__':
    app.run(threaded=True)