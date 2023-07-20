<b> Project name: </b> <br>
Customized Warning System for MQTT realtime data

<b> Description: </b> <br>
The warning system is a critical component designed to monitor real-time data against user-defined configurations stored in MongoDB. It subscribes to MQTT topics to observe data and promptly sends warnings to the UI web when data exceeds predefined thresholds. Simultaneously, warning records are stored in MongoDB for historical tracking and analysis. This system ensures proactive alerts and enables quick responses to potential risks and critical events.

<b> 1. System diagram: </b><br>
The interaction among the warning system, MQTT broker, MongoDB, Django, UI web, and Kafka can be described as follows:<br><br>
MQTT Broker: The MQTT broker serves as a message broker that facilitates communication between different components of the warning system. It allows devices and applications to publish and subscribe to specific topics to exchange data.<br><br>
Warning System: The warning system is the core component that processes and manages warning-related tasks. It is responsible for handling incoming data, computing warning conditions, and triggering warning events when necessary.<br><br>
MongoDB: MongoDB is a NoSQL database used by the warning system to store and manage warning configurations, historical data, and other relevant information.<br><br>
Django: Django is a Python-based web framework that provides the backend for the UI web. It handles user requests, interacts with MongoDB to retrieve warning configurations, and updates warning settings based on user inputs.<br><br>
UI Web: The user interface (UI) web is the frontend part of the system that users interact with. It allows users to view warning settings, update configurations, and monitor warning events visually.<br><br>
Kafka: Kafka is a distributed event streaming platform that enables high-throughput, real-time data processing and communication between different components of the system.<br><br>

<b> 2. Introduction to the Warning System Function:</b> <br>
Init.py: The system will check the connection and set up default settings. After establishing a connection, the system will query the warning configuration from MongoDB using Django.<br><br>
Api.py: Users can update the warning configuration on the UI web and send requests to the system to update the warning settings. Simultaneously, the latest warning configuration will be saved into MongoDB.<br><br>
Query.py: The system has a schedule to check the connection. Once reconnected to the internet, the system will query the latest warning configuration.<br><br>
MQTT_Handler.py: This module handles the connection with the MQTT broker and allows subscribing/unsubscribing to topics.<br><br>
Warning_Method.py: This module computes and observes data based on thresholds for each warning rule and condition.<br><br>
Warning_Event.py: This module sends warning data when it exceeds the threshold and is not within the silence_interval time. If the system loses connection, it will record data and send the warning data after re-establishing the connection.<br><br>
![png](https://github.com/marx1992620/WarningSystem/blob/main/system_diagram.png) <br>

<b>3. Warning Config:</b> <br>
At the UI web interface, users can set up the warning configuration, which includes machine information, warning rules, thresholds, conditions, silent intervals, and more. The warning config is flexible, supporting multiple warning rules and trigger conditions to cater to various monitoring scenarios. <br>
![png](https://github.com/marx1992620/WarningSystem/blob/main/warning_config.png) <br>

<b>4-1. Warning System (Initial) Log:</b> <br>
The system will first check the connection. Once the connection is established, it will proceed to set up the default settings and connect to the MQTT broker. Afterward, it will query the warning configuration from MongoDB and subscribe to the MQTT topics to observe real-time data. <br>
![png](https://github.com/marx1992620/WarningSystem/blob/main/warning_system_init.png) <br>

<b>4-2. Warning System (Warning) Log:</b> <br>
The system receives real-time data via MQTT and checks each rule and condition against predefined thresholds. When the MQTT data exceeds the threshold, the Warning System sends warning data to the UI web and saves the warning record into MongoDB. During the silence_interval, the system refrains from sending additional warning data but continues to keep records of the data. <br>
![png](https://github.com/marx1992620/WarningSystem/blob/main/warning_system_log.png) <br>

<b>5. Warning Record:</b> <br>
The warning data, containing information about the machine, warning rule, warning data, and warning time, is loaded into MongoDB as follow snapshot. <br>
![png](https://github.com/marx1992620/WarningSystem/blob/main/warning_record.png) <br>
