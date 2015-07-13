#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
import os
from datetime import datetime
class Memory():
    def __init__(self,datapath,name):
        self.__datapath = datapath
        self.__name = name
        self.__memory = {}
        self.load()
        
    # load dict from file
    def load(self): 
        print "trying to load existing memory file"   
        try:  
            with open(self.__datapath + os.sep +self.__name+".mem","r") as file:
                self.__memory =  json.loads(file.read())
                print("Memory %s successfully loaded"%self.__name)
        except Exception,e:
            print("Memory '%s' does not exist. This is normal on first execution. %s",self.__name,str(e))
    
    # save dict in file
    def save(self): 
        with open(self.__datapath+os.sep+self.__name+".mem","w") as file:
            file.write(json.dumps(self.__memory,default=self.json_serial))
        print("Memory %s saved successfully"%self.__name)
    
    # returns a list of the keys of the dict, return [] if no keys
    def getKeys(self):
        return self.__memory.keys()    

    def hasKey(self,key):
        return key in self.__memory
    
    def getData(self,key):
        if self.hasKey(key):
            return self.__memory.get(key)
        else :
            print("key does not exist in memory: %s"%key)
            return None
    
    def insertData(self,key,data):
        if self.hasKey(key):
            self.__memory[key] = data
        else :
            print("key '%s' did not exist in memory, new key inserted !"%key)
            self.__memory[key] = data

    # insert new entries
    def insertDatas(self,new_dict):
        self.__memory.update(new_dict)
    
    def removeData(self,key):
        if self.hasKey(key):
            self.__memory.pop(key)
            return True
        else:
            return False
        
    
    def json_serial(self,obj):
        """JSON serializer for objects not serializable by default json code"""
        
        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError ("Type not serializable")

if __name__=="__main__":    
    
    datapath = "."
    name = "memory_bob"
    mem = Memory(datapath,name)
    
    print "1-dict from memory is ", mem.getKeys()
    mem.insertData("straw2", 15) 
    mem.insertData("banana", []) 
    print "2-dict is now " ,mem.getKeys()
    D = {"kiwi": 42,"mangue": 24, "litchi": 64}
    mem.insertDatas(D)
    print "3-dict is now " ,mem.getKeys()
    print "has key straw2",mem.hasKey("straw2")
    print "Removing item",mem.removeData("straw2")
    print "has key straw2",mem.hasKey("straw2")
    print "4-dict is now " ,mem.getKeys()
    print "Removing item",mem.removeData("straw2")
    print "key is", mem.getData("mangue")


