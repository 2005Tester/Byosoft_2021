#  Copyright (c) 2020, Byosoft Corporation.<BR>
#  All rights reserved.This software and associated documentation (if any)
#  is furnished under a license and may only be used or copied in
#  accordance with the terms of the license. Except as permitted by such
#  license, no part of this software or documentation may be reproduced,
#  stored in a retrieval system, or transmitted in any form or by any
#  means without the express written consent of Byosoft Corporation.

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header


class EmailReport():
    def __init__(self, smtpserver, sender, receiver, pw, _subtype='octet-stream'):
        self.smtpserver = smtpserver
        self.sender = sender
        self.receiver = receiver
        self.pw = pw

    def send_mail(self, html_report, attachment):
        message = MIMEMultipart()
        message_html = MIMEText(html_report, "html", "utf-8")
        message.attach(message_html)
        message['From'] = 'Byosoft Automation Test'
        message['To'] = Header(self.receiver)
        message['Subject'] = 'Haiyan5 Automation Test'
        if os.path.exists(attachment):
            logging.info("Adding attachment")
            with open(attachment,'rb') as f:
                attachfile = MIMEApplication(f.read())
                attachfile.add_header('Content-Disposition', 'attachment', filename=attachment)
                message.attach(attachfile)

        try:
            smtpObj = smtplib.SMTP() 
            smtpObj.connect(self.smtpserver,25)
            smtpObj.login(self.sender,self.pw) 
            smtpObj.sendmail(self.sender,self.receiver.split(','),message.as_string()) 
            smtpObj.quit() 
            logging.info('Email sent successfully.')
        except smtplib.SMTPException as e:
            logging.error('Failed to send email report.',e)


