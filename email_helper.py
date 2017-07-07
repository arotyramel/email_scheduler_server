#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import smtplib, email
from email import parser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.header import decode_header
from email import Encoders

from email.header import Header
from email.utils import formataddr,parseaddr

import time
from threading import Lock
import imaplib
import re

class EmailHelper():
    def __init__(self):
        self.mutex = Lock()
        self.busy = 0
        self.imap = False
        self.smtp = False
        self.__userid = None
        self.__password = None
        self.smtpServer = smtplib.SMTP("smtp.gmail.com",587)
        

    def setLoginData(self,user,pw):
        if not self.isAddressValid(user):
            return False
        self.__userid = user
        self.__password = pw
        return True
        
    def isAddressValid(self,receiver):
        if not re.match(r"[^@]+@[^@]+\.[^@]+",receiver):
            print ("EMail address not valid")
            return False
        else:
#             print "Email address is valid"
            return True

    def sendMail(self,sender,receiver,subject,text=None,attach_name=None):
        if not self.isAddressValid(receiver):
            return False
        msg=MIMEMultipart()
        sender = formataddr((str(Header(unicode(sender), 'utf-8')), self.__userid))
        msg['From']=sender
        print (sender)
        msg['To']=receiver
        msg['Date']=email.Utils.formatdate(localtime=True)
        msg['Subject']=subject
        
        msg.attach(MIMEText(text, "html"))
        msg = self.attachFile(attach_name,msg)        
        
        
        if not self.smtp:    
            print ("not logged in smtp")
            return   
        self.smtpServer.sendmail(self.__userid, receiver, msg.as_string())

        
    def attachFile(self,filename,msg):
        if filename is None or filename == "" or filename == []:
            return msg
            
        if type(filename) is list:
            for file in filename:
                msg = self.attachFile(file,msg)
        else:    
            fp = open(filename,"rb")
            part = MIMEApplication(fp.read())
            fp.close()
            #take only name and not full path for attachment name
            part.add_header('Content-Disposition', 'attachment', filename=filename)
            print ("attaching file :",filename)
            msg.attach(part)
        return msg

    def exit(self):#not required any more as connection is closed after every mail
        self.logoutSmtp()
        self.logoutImap()

    def waitUntilFinished(self, timeout=20):
        time.sleep(1)
        start = time.time()
        end = time.time()+timeout
        while start < end:
            start = time.time()
            with self.mutex:
                if self.busy <= 0:
                    return
            time.sleep(0.5)
        print ("timeout reached while waiting for finishing the task")
    
    def login(self):
        if self.loginImap() and self.loginSmtp():
            return True
        else:
            return False

    def logout(self):
        if self.logoutImap() and self.logoutSmtp():
            return True 
        else:
            return False
    
    def loginSmtp(self):
        try:
            if not self.smtp:
                self.smtpServer = smtplib.SMTP("smtp.gmail.com",587)
                self.smtpServer.ehlo()
                self.smtpServer.starttls()
                self.smtpServer.ehlo()
                self.smtpServer.login(self.__userid ,self.__password)
                self.smtp = True
            return True
        except Exception as e:
            print (e)
            return False
            
    def logoutSmtp(self):
        try:
            if self.smtp:
                self.smtpServer.quit()
                self.smtp = False
            return True
        except:
            return False
        
    def logoutImap(self):
        try:
            if self.imap:
                self.imapServer.close()
                self.imapServer.logout()
                self.imap = False
            return True
        except:
            return False
  
    def loginImap(self):
        try:
            if not self.imap:
                self.imapServer = imaplib.IMAP4_SSL('imap.gmail.com')
                self.imapServer.login(self.__userid, self.__password)
                self.imap = True
            return True
        except Exception as e:
            print (e)
            return False
    
    def fetchEmails(self,evaluate=True):
        print ("fetching emails")
        self.imapServer.select("inbox")
        result, data1 = self.imapServer.search( None, 'ALL')#'UNSEEN'
        messages = []
        for num in data1[0].split():
            typ, data2 = self.imapServer.fetch(num, '(RFC822)')
            for response_part in data2:
                if evaluate:
                    msg_part = self.evaluateMessage(response_part)
                    if not msg_part == None:
#                         print "appending ", msg_part
                        messages.append(msg_part)
                else:
                    messages.append(response_part)        
        return messages
        
    def evaluateMessage(self,response_part):
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1])
            varSubject = decode_header(msg['subject'])[0][0]
            varFrom = decode_header(msg['from'])[0][0]
#             print varFrom
#             varFrom = varFrom.replace('<', '')
#             varFrom = varFrom.replace('>', '')
            resp = parseaddr(varFrom)
#             print resp
            (sender_name, varFrom) = resp
            [message,attachment] = self.extractMessageBody(msg)
            date = msg['Date']
            print ("date",date)
            return [varFrom,varSubject,message,date,attachment,sender_name]
        return None

    def extractMessageBody(self,msg):
        text = ""
        filename = None
        if msg.is_multipart():
            html = None
            
#             for part in msg.get_payload():
            for part in msg.walk():
                ctype = part.get_content_type()
#                 print "%s,%s" % (ctype,part.get_content_charset())
     
              
                if ctype == 'text/plain':
                    charset = part.get_content_charset()
                    text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                    continue
                
                if ctype == 'text/html':
                    charset = part.get_content_charset()
                    html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                    continue
                
                if not part.get('Content-Disposition') is None:
#                     print "attachment found"
                    filename = part.get_filename()
                    filename = decode_header(filename)[0][0]
                    
                    with open(filename, 'wb') as fp:
                        fp.write(part.get_payload(decode=True))
#                     print '%s saved!' % filename
                    continue
                if part.get_content_charset() is None:
                    # We cannot know the character set, so return decoded "something"
                    text = part.get_payload(decode=True)
                    continue
     
                    
            if text is not None:
                return [text.strip(),filename]
            else:
                return [html.strip(),filename]
        else:
            text = unicode(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore').encode('utf8', 'replace')
            return [text.strip(),filename]
    
    def deleteMailByDate(self,date):
        self.imapServer.select("inbox")
        typ, data1 = self.imapServer.search(None, 'ALL')
        for num in data1[0].split():
            typ, data2 = self.imapServer.fetch(num, '(RFC822)')
            for response_part in data2:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1])
                    if date == msg['Date']:
                        self.imapServer.store(num, '+FLAGS', '\\Deleted')
                        self.imapServer.expunge()
                        return
                    
    def deleteAllEmails(self):
        self.imapServer.select("inbox")
        typ, data = self.imapServer.search(None, 'ALL')
        for num in data[0].split():
            self.imapServer.store(num, '+FLAGS', '\\Deleted')
        self.imapServer.expunge()
        





