#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from email_helper import EmailHelper

from email.header import decode_header
import memory

import time
import sys
from datetime import datetime

try:
    from dateutil.relativedelta import relativedelta
except:
    print "pip install python-dateutil"
    exit()

class EmailScheduleServer():
    def __init__(self, user, pw,admin,shopper=[]):
        self.id = "Mail Robot"
        self.admin = admin
        self.shopper = shopper
        self.datapath = sys.argv[0].rsplit("/",1)[0]
        print "Datapath set to:",self.datapath
        self.memory = memory.Memory(self.datapath,"email_server")
        self.eh = EmailHelper()
        self.eh.setLoginData(user, pw)
        self.cart_send = False
         
    def saveMail(self,sender,body,date,sender_name):
        self.memory.insertData(date,[sender,body,sender_name])

    def checkForNewJobs(self):
        msgs = self.eh.fetchEmails(True)
        for msg in msgs:#[from,subject,message body,date,attachmentname,sender_name]
            
            try:
                if msg[1]=="**newrobotjob":
                    if not self.memory.hasKey(msg[3]):
                        content = self.extractDataFromBody(msg[2])
                        if not self.eh.isAddressValid(content["receiver"]):
                            failmsg = ["FAIL: Job not added","Invalid recepient address provided. Job skipped"]
                            self.sendFail(msg[0],*failmsg)
                        if content["message"]=="":
                            failmsg = ["FAIL: Job not added","Message body seems to be empty"]
                            self.sendFail(msg[0],*failmsg)
                        else: #everything seems fine
                            content["attachment"] = msg[4]
                            self.saveMail(msg[0],content,msg[3],msg[5])
                            self.sendConfirmation(msg[3])
                elif msg[1]=="**shopping":
                    self.updateShoppingCart(msg[0],msg[2])
                elif msg[1]=="**mask":
                    self.sendMask(msg[0])
                else:#check for keywords in current jobs and send response
                    key = self.validKeywordFound(msg)
                    if not key is None:
                        data = self.memory.getData(key)
                        self.eh.sendMail(msg[5],data[0],data[1]["subject"],msg[2])
                        self.memory.removeData(key)                   
                    else:
                        print "unknown email received"
                        print "transfering to admin"
                        self.transferMessageToAdmin(msg)
                        print "msg",msg
                self.eh.deleteMailByDate(msg[3])
            except Exception,e:
                print "evaluating new email job failed!"
                print e



    def executeAllJobs(self):
        for key in self.memory.getKeys():
#             print key
            if key.startswith("**"):
                continue 
            try:

                sender = self.memory.getData(key)[2]
                content = self.memory.getData(key)[1]
                print content["timeToSend"]-time.time()
                if time.time() > content["timeToSend"] and content["timeToSend"] > 0:
#                     print "attachment",content["attachment"]
                    print "sending emails"
                    self.eh.sendMail(sender,content["receiver"],content["subject"],content["message"],content["attachment"])
                    if content["interval"] < 0:
                        content["timeToSend"] = -1
                        if content["keyword"] == "":
                            print "deleting memory entry"
                            self.memory.removeData(key)
                    else:
                        content["timeToSend"]+=content["interval"]
#                
            except Exception,e:
                print "Email could not be parsed correctly. Skipping"
                print e
                 
    
    def start(self):
        print "email schedule server started"
        while True:
            try:
                print datetime.now()
    #             print "checking for new jobs"
                self.eh.login()
                self.checkForNewJobs()
    #             print "executing jobs"
                self.executeAllJobs()
                self.sendShoppingCart()
                self.eh.logout()
    #             break
                if not self.memory.save():
                    print "could not save the memory. exiting application"
                    break
                print "--------------------------"
    #             print "waiting for next iteration"
            except Exception,e:
                print e
                
            time.sleep(60)
        self.close()
            
                
    def getTimeDiff(self,i):
        for v in i:#check if string represents valid integer value
            if not v.isdigit():
                return -1
        i = [int(x) for x in i]
        while len(i) < 6:
            i.append(0)
        print "get delta from ",i
        delta = relativedelta(years=i[0],months=i[1],days=i[2],hours=i[3],minutes=i[4],seconds=i[5])
        now = datetime.now()
        return ((now+delta)-now).total_seconds() #stupid python -.-
            
     
    def validKeywordFound(self,msg):
#         print msg
        for key in self.memory.getKeys():
            if key.startswith("**"):
                continue
            keyword = self.memory.getData(key)[1]["keyword"]
#             print "keyword",keyword 
            if keyword == "":
                return None
            for part in msg:
#                 print "part",part
                if part is None:
                    continue
                if part.lower().find(keyword.lower()) != -1:
                    return key
        return None
    
    def extractDataFromBody(self,body):
        print "extracting info from body"
        tag = ["**","/**"]
        items = ["receiver","subject","message","keyword","interval","timeToSend"]
#         print "body before cut",body
        body = self.find_between(body, "---", "---")
        content = {}
        print "after cut ", body
        for i in range(len(items)):
            content[items[i]] = self.find_between(body, tag[0]+items[i]+":", tag[1])
            
        content["keyword"] = content["keyword"].strip() 
            
        if content["interval"].find("-") != -1:
            content["interval"] = self.getTimeDiff(content["interval"].split("-"))
        else:
            content["interval"] = -1
            
        if content["timeToSend"].find("-") != -1:
            
            content["timeToSend"] =self.maketime(content["timeToSend"].split("-")) 
        else:
            content["timeToSend"]=time.time()
        
        return content
        
    def maketime(self,t):
        print t
        t = [int(x) for x in t]
        while len(t) < 9:
            t.append(0)
        print "requested time ",time.mktime(t)+time.timezone
        print "now",time.time()
        return time.mktime(t)+time.timezone
        
    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
    
    
    def sendConfirmation(self,id):
        print "sending confirmation"
        sender = self.memory.getData(id)[0]
        msg = "Your request has been added to the email schedule server. You will get your answer, when it is available."
        self.eh.sendMail(self.id,sender,"New scheduled job has been added",msg)
        
    def sendFail(self,sender,subject,failmsg):
        self.eh.sendMail(self.id,sender,subject,failmsg)
        
    def sendMask(self,sender):
        subject = "Required mask to add a new job to the email scheduler"
        mask="""
        Use '**newrobotjob' as subject to be recognized.
        Copy the following formated example into your message and change the values according to your needs. Attached files will also be transfered.
        ---
        **receiver:someone@gmail.com/** Den finalen Empfänger
        **subject:Reparaturanfrage/** Betreff
        **message:Wieso ist mein Computer immer noch kaputt? Bitte um unverzügliche Antwort!/** Nachricht an den Empfänger
        **keyword:someone/** Wird dieses Schlüsselwort in einem eingehenden Email gefunden, wird die Antwort transferiert
        **interval:0000-00-00-00-02/**  YYYY-MM-DD-HH-MM-SS In welchem Intervall,also wie oft, soll das Email gesendet werden?
        **timeToSend:now/** now oder YYYY-MM-DD-HH-MM-SS Wann soll das Email das erste Mal gesendet werden.
        ---
        """ 
        self.eh.sendMail(self.id,sender,subject,mask)
        
    def transferMessageToAdmin(self,msg):
        self.eh.sendMail(self.id,self.admin,"Unknown email received from "+msg[0]+" with topic: "+msg[1],msg[2],msg[4])

    def listSavedEmails(self):
        for key in self.memory.getKeys():
            print self.memory.getData(key)
    
    def updateShoppingCart(self,sender,body):
        shoppingCart = body.split("\n")
        shoppingCart = [x.rstrip("\r").decode("utf-8-sig") for x in shoppingCart]
        if self.memory.hasKey("**shoppingCart"):
            shoppingCart+=(self.memory.getData("**shoppingCart"))
        shoppingCart = list(set(shoppingCart))
        self.memory.insertData("**shoppingCart",shoppingCart)
        msg="<html><body>"
        msg+= "<br>".join([x.encode("utf-8") for x in shoppingCart])
        msg+="</body></html>"        
        self.eh.sendMail(self.id,sender,"Current shopping cart",msg)

    def sendShoppingCart(self):
        weekday = datetime.today().weekday()
        if weekday == 4 and self.cart_send is False and time.strftime("%H")=="12":
            self.cart_send = True
            if self.memory.hasKey("**shoppingCart"):
                shoppingCart+=(self.memory.getData("**shoppingCart"))
            else:
                print "There is nothing in your shopping cart"
                return
            msg="<html><body>"
            msg+= "<br>".join([x.encode("utf-8") for x in shoppingCart])
            msg+="</body></html>"         
            for shopper in self.shopper:
                self.eh.sendMail(self.id,shopper,"Current shopping cart",msg)
            self.memory.removeData("**shoppingCart")
        if weekday != 4:
            self.cart_send = False
        
            
        

    def close(self):
        self.memory.save()



if __name__=='__main__':
    from config import *
    ess    = EmailScheduleServer(USER,PASSWORD,ADMIN,SHOPPER)
    ess.start()
    ess.close()
    print "email schedule server closed"

