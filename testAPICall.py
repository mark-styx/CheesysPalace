import requests,json
from datetime import datetime as dt

from requests.api import request

class Connection:
    def __init__(self):
        self.token = False
        self.call_history = {}
        self.connectionId = str(int(dt.now().timestamp()))
        self.url = 'https://wap.tplinkcloud.com'
        self.login()

    def call(self,method='post',payload={},endpoint=''):
        if self.token:
            if payload.get('params'):payload['params'].update({'token':self.token})
            else: payload.update({'params':{'token':self.token}})
        else: pass
        self.response = requests.request(
            method=method,
            data=json.dumps(payload),
            url=f'{self.url}/{endpoint}',
            headers={
                'Content-Type':'application/json',
                'User-Agent':'Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/M4B30X)'
                }
        )
        self.call_history.update(
            {
                dt.now().timestamp():{
                    'response':self.response,
                    'method':method,
                    'payload':json.dumps(payload),
                    'url':f'{self.url}/{endpoint}'
                    }
                }
            )

    def login(self,usr='mark.styx@hotmail.com',pwd='192837465Meowowow'):
        self.call(
            payload={
                'method':'login',
                'params':{
                    'appType':'Kasa_Android',
                    'cloudUserName':usr,
                    'cloudPassword':pwd,
                    'terminalUUID':self.connectionId
                }
            }
        )
        self.token = self.response.json().get('result').get('token')



class SmartHub:
    def __init__(self):
        self.devices = {}
        self.connection = Connection()
        self.get_devices()

    def package_live_devices(self):
        keys = dict.fromkeys([x.deviceName for x in self.devices.values() if x.status])
        for key in keys:
            keys.update({key:[x.alias for x in self.devices.values() if x.status and x.deviceName == key]})
        return keys

    def get_devices(self):
        self.connection.call(
            payload={'method':'getDeviceList'}
        )
        for device in self.connection.response.json().get('result').get('deviceList'):
            self.devices.update(
                {
                    device.get('alias'):{
                        'IOT.SMARTPLUGSWITCH':Switch,
                        'IOT.SMARTBULB':LightBulb,
                        'IOT.IPCAMERA':Device
                    }[device.get('deviceType')](device,self.connection)
                }
            )
        self.live_devices = self.package_live_devices()


class Device:
    def __init__(self,params,connection):
        self.__dict__.update(params)
        self.connection = connection
        self.command_history = {}

    def log_command(self,command):
        self.command_status = 0 if self.connection.response.json().get('error_code') else 1
        self.command_history.update(
            {
                str(dt.now()):{
                    command:{
                        'status':self.connection.response.status,
                        'successful':self.command_status
                        }
                    }
                }
            )

    def get_system_info(self):
        response = self.call("{\"system\":{\"get_sysinfo\":1}}")
        self.__dict__.update(json.loads(self.connection.response.json().get('result').get('responseData')).get('system').get('get_sysinfo'))
        
    def call(self,requestData):
        self.connection.call(
            payload={
                'method':'passthrough',
                'params':{
                    'deviceId':self.deviceId,
                    'requestData':requestData
                }
            }
        )
        return self.connection.response


class LightBulb(Device):
    def __init__(self,params,connection):
        super().__init__(params=params,connection=connection)
        self.get_system_info()

    def alter_state(self,power=None,color_temp=None,brightness=None):
        if power is None:power = self.light_state.get('on_off')
        if self.light_state.get('dft_on_state'):
            if color_temp is None:color_temp = self.light_state.get('dft_on_state').get('color_temp')
            if brightness is None:brightness = self.light_state.get('dft_on_state').get('brightness')
        if color_temp is None:color_temp = self.light_state.get('color_temp')
        if brightness is None:brightness = self.light_state.get('brightness')
        requestData="{\"smartlife.iot.smartbulb.lightingservice\":{\"transition_light_state\":{\"on_off\":%s,\"ignore_default\":1,\"transition_period\":1,\"color_temp\":%s,\"brightness\":%s}}}}" % (
            power,color_temp,brightness
        )
        self.call(requestData)
        self.get_system_info()


class Switch(Device):
    def __init__(self,params,connection):
        super().__init__(params=params,connection=connection)

    def alter_state(self,power):
        self.connection.call(
            payload={
                'method':'passthrough',
                'params':{
                    'deviceId':(self.deviceId),
                    "requestData":"{\"system\":{\"set_relay_state\":{\"state\":" + str(power) + "}}}"
                }
            }
        )
        self.status = power


