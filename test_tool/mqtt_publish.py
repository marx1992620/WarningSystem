import paho.mqtt.client as mqtt
import random
import json  
import datetime 
import time

ISOTIMEFORMAT = '%m/%d %H:%M:%S'  # 設置日期時間的格式



# 連線設定
client = mqtt.Client()  # 初始化地端程式
client.username_pw_set("account","pwd")  # 設定登入帳號密碼
client.connect("127.0.0.1", 1883, 60)  # 設定連線資訊(IP, Port, 連線時間)

while True:
    timestamp = time.time()
    r = random.randint(0,5)
    data1 = {"timestamp":timestamp,"value":[0,1,0,1,r]}
    data2 = {"timestamp":timestamp,"name":"motor","value":{"director":1,"pulse":20*r}}

    #要發布的主題和內容
    client.publish("/Devices/work_station_1/Digital", json.dumps(data1), 0, False)  # topic, payload, qos, retain
    client.publish("/Devices/inside_transfer_2/PWM", json.dumps(data2), 0, False)  # topic, payload, qos, retain
    time.sleep(1.5)
    print(r,timestamp)

    # 準備要傳送的訊息
    messages = [
    {'topic':"/Devices/work_station_1/Digital", 'payload':data1, 'qos':0, 'retain':False},
    {'topic':"/Devices/inside_transfer_2/PWM", 'payload':data2, 'qos':0, 'retain':False},
    ]

    # 一次發布多則 MQTT 訊息
    # client.publish.multiple(
    # messages,
    # hostname="mqtt.example.com",
    # port=1883,
    # auth={'username':'myuser','password':'mypassword'})