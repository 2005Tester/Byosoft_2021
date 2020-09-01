# -*- encoding=utf8 -*-
import requests
import json

headers = {
    'If-Match': 'W/"584db857"',
    'Authorization': 'Basic QWRtaW5pc3RyYXRvcjpBZG1pbkA5MDAw',
    'Content-Type': 'application/json'
    }


def get(url):
    response = requests.request("GET", url, headers=headers, verify=False)
    result = response.text
    response.close()
    return result


# 发送PATCH request 设置 testcase里面的值
def patch_tc_file(testcase_file, url):
    with open(testcase_file, 'r') as fp:
        payload = json.load(fp)
    response = requests.request("GET", url, headers=headers, verify=False)
    etag = response.headers['ETag']
    headers['If-Match'] = etag
    response = requests.request("PATCH", url, headers=headers, data=payload, verify=False)
    response.close()
    return response.text.encode('utf8')


def patch_single_payload(payload, url):
    # Payload 格式: payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%s\" \r\n    }\r\n}" %(key, value)
    # key = list(payload["Attributes"].keys())[0]
    # value = payload["Attributes"][key]
    # if isinstance(value, int):
    #    payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%d\" \r\n    }\r\n}" %(key, value)
    # else:
    #    payload = "{\r\n    \"Attributes\": {\r\n     \"%s\": \"%s\" \r\n    }\r\n}" %(key, value)
    response = requests.request("GET", url, headers=headers, verify=False)
    etag = response.headers['ETag']
    headers['If-Match'] = etag
    response = requests.request("PATCH", url, headers=headers, data=payload, verify=False)
    response.close()
    return response.text.encode('utf8')


def post_req(url):
    response = requests.request("POST", url, headers=headers, verify=False)
    result = response.text
    response.close()
    return result
