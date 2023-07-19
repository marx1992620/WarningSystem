from confluent_kafka import Consumer, KafkaException
import json
n = 0
def consume():
    # broker = "172.28.146.46:9093"
    global n
    broker = "172.28.146.46:9093"
    group = "123"
    topics = ["/Devices/work_station_1/Digital","/Devices/inside_transfer_2/PWM"]
    topics = [i[1:].replace("/","-") for i in topics]
    print(topics)

    conf = {'bootstrap.servers': broker, 'group.id': group, 'session.timeout.ms': 60000,
            # 'default.topic.config' : {'auto.offset.reset': 'largest'},
            'auto.offset.reset': 'largest'}
    
    
    #Kafka subscribe topics
    kafkaClient = Consumer(conf)
    kafkaClient.subscribe(topics)
    print(f"kafkaClient subscribe {topics}")

    while True:

        data = kafkaClient.consume(num_messages=1000,timeout=1)
        if data is None:
            continue

        else:
            # print(datetime.now(),">>>",len(data),"data")
            for msg in data:
                # if msg.error():
                #     raise KafkaException(msg.error())
                kafka_data = msg.value().decode("utf-8")
                json_data = json.loads(kafka_data)
                print(json_data)
                n += 1 
                print("numbers: ",n)
                # print(json_data)

consume()