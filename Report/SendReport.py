#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from json2html import *
import json


def json_to_html():
    dict_str = open('result.json','r',encoding='utf-8').read()
    data_dict = json.loads(dict_str)
    data_xml = json2html.convert(data_dict)
    # data_xml = json2html.convert(json=data_dict, table_attributes="id=\"info-table\" class=\"table table-bordered table-hover\"")
    print("data_xml", data_xml)
    html_head = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    {}
    </body>
    </html>'''
    result_html = html_head.format(data_xml)
    return result_html


def send_report():
    from_addr = 'ci@byosoft.com.cn'
    password = 'byosoft@ci123'
    to_addr = 'gaojie@byosoft.com.cn'
    report = json_to_html()

    #print(report)
    message = MIMEText(report, "html", "utf-8")
    #print(message)

    smtp_server = 'mail.byosoft.com.cn'
 


    message['From'] = 'Byosoft Automation Test'
    message['To'] = Header(to_addr)
    message['Subject'] = 'Haiyan5 Automation Test'



    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(smtp_server,25)
        smtpObj.login(from_addr,password) 
        smtpObj.sendmail(from_addr,to_addr,message.as_string()) 
        smtpObj.quit() 
        print('success')
    except smtplib.SMTPException as e:
        print('error',e)


if __name__ == '__main__':
    send_report()



