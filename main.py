#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from email_server import EmailScheduleServer


if __name__=='__main__':
    from config import *
    ess    = EmailScheduleServer(USER,PASSWORD,ADMIN)
    ess.start()
    ess.close()
    print "email schedule server closed"
