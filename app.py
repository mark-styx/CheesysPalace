import json
from flask import Flask,render_template,request,after_this_request
from testAPICall import SmartHub

SH = SmartHub()
SH.get_devices()
app = Flask(__name__)

@app.route('/', methods=['get'])
def home():
    return render_template('cheesys_palace.html')

@app.route('/check_devices',methods=['get'])
def get_iot_devices():
    return json.dumps(SH.live_devices)

@app.route('/device_action/<deviceAlias>/<action>/<int:state>',methods=['post'])
def device_action(deviceAlias,action,state):
    SH.devices.get(deviceAlias).alter_state(**{action:state})
    @after_this_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    jsonResp = {'status':200,'params':[deviceAlias,action,state]}
    return jsonResp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')