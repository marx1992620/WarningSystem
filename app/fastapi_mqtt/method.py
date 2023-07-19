import logging


def check_value(payload,method,threshold):

    data_type = type(payload)
    if method == "eq":
        if data_type == type(list()):
            for value in payload:
                if value == threshold:
                    return True
        elif data_type in [type(int()),type(float()),type(str())]:
            if payload == threshold:
                return True
            
    elif method == "neq":
        if data_type == type(list()):
            for value in payload:
                if value != threshold:
                    return True
        elif data_type in [type(int()),type(float()),type(str())]:
            if payload != threshold:
                return True
            
    elif method == "gt":
        if data_type == type(list()):
            for value in payload:
                if value > threshold:
                    return True
        elif data_type in [type(int()),type(float()),type(str())]:
            if payload > threshold:
                return True
            
    elif method == "gte":
        if data_type == type(list()):
            for value in payload:
                if value >= threshold:
                    return True
        elif data_type in [type(int()),type(float()),type(str())]:
            if payload >= threshold:
                return True
            
    elif method == "lt":
        if data_type == type(list()):
            for value in payload:
                if value < threshold:
                    return True
        elif data_type in [type(int()),type(float()),type(str())]:
            if payload < threshold:
                return True

    elif method == "lte":
        if data_type == type(list()):
            for value in payload:
                if value <= threshold:
                    return True
        elif data_type in [type(int()),type(float()),type(str())]:
            if payload <= threshold:
                return True
    return False


def extract_payload(payload,compute_method):
    if compute_method == "sum":
        payload = sum(payload)

    elif compute_method == "mean":
        payload = sum(payload)/len(payload)

    elif compute_method == "max":
        payload = max(payload)

    elif compute_method == "min":
        payload = min(payload)

    else:
        return payload

    return payload


def template_match(payload,topic,each_condition):
    from fastapi_mqtt.fast_mqtt import FastMQTT
    result = []
    compare_method,threshold,template,compute_method = each_condition["compare_method"],each_condition["threshold"],each_condition["template"],each_condition["compute_method"]

    if topic not in FastMQTT.topic_payload:
        FastMQTT.topic_payload[topic] = payload
        return False
    elif len(FastMQTT.topic_payload[topic]) < 2*len(payload) or len(FastMQTT.topic_payload[topic]) <= len(template):
        FastMQTT.topic_payload[topic] += payload

    elif len(FastMQTT.topic_payload[topic]) > len(template):
        # if len(FastMQTT.topic_payload[topic]) > 3*len(payload) and len(FastMQTT.topic_payload[topic]) - len(payload) > len(template):
        #     FastMQTT.topic_payload[topic] = FastMQTT.topic_payload[topic][len(payload):]
        FastMQTT.topic_payload[topic] = FastMQTT.topic_payload[topic][len(payload):]
        FastMQTT.topic_payload[topic] += payload

    if len(template) >= len(FastMQTT.topic_payload[topic]):
        return False

    # print("\n@@@@@@@@@@")
    # print(FastMQTT.topic_payload[topic])
    w = 0
    while len(template)+w <= len(FastMQTT.topic_payload[topic]):
        piece_payload = FastMQTT.topic_payload[topic][0+w : len(template)+w]
        payload_diff = [piece_payload[i] - template[i] for i in range(len(template))] # list substract list
        # print(piece_payload)
        # extract_data from payload_diff
        extract_data = extract_payload(payload_diff,compute_method)
        # if type(extract_data) == type(list()):
        #     data_type = type(list())
        # else:
        #     data_type = type(int())
        try:
            result = check_value(extract_data,compare_method,threshold)
        except Exception as e:
            logging.error(f"check_value occurs error as {e}")
        if result == True:
            print(extract_data,compare_method,threshold)
            # FastMQTT.topic_payload[topic] = FastMQTT.topic_payload[topic][len(template):]
            return result
        else:
            piece_payload = []
            w+=1

    # FastMQTT.topic_payload[topic] = FastMQTT.topic_payload[topic][len(template):]
    return False


def methods(payload,topic_dic):

    warning_condition,condition = topic_dic["warning_condition"],topic_dic["condition"]
    result = []

    for each_condition in condition:
        if len(each_condition.get("template","")) > 0:
            topic = topic_dic["topic"]
            result.append(template_match(payload,topic,each_condition))

        else:
            compare_method = each_condition["compare_method"]
            threshold = each_condition["threshold"]
            try:
                result.append(check_value(payload,compare_method,threshold))
            except Exception as e:
                logging.error(f"check_value occurs error as {e}")
    if warning_condition == "or" and True in result:
        return True
    elif warning_condition == "and" and False not in result:
        return True
    else:
        return False
