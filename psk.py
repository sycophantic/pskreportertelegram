#!/usr/bin/python3

from settings import CALLSIGN, APIKEY, CHATID
from bs4 import BeautifulSoup
from pathlib import Path
import datetime
import time
import requests

seconds=-600
heardtime=0

while True:
    #api gives a 403 if you don't set a useragent
    headers = {'User-Agent': 'pskreportertelegram python script'}
    #build query url
    url = "https://retrieve.pskreporter.info/query?senderCallsign=" + CALLSIGN + "&rronly&flowStartSeconds=" + str(seconds)
    print("Querying pskreporter for " + CALLSIGN)
    result=requests.get(url, headers=headers)
    txt=result.content.decode()
    #check if you are requesting data too fast
    if "moderate" in txt:
        print(txt)

    #load from file for testing
    #txt = Path('testdata').read_text()
    
    soup = BeautifulSoup(txt, 'lxml')
    
    #find all reception reports
    reports=soup.find_all('receptionreport')
        
    #grab newest heard time
    
    if len(reports) > 0:
        newheardtime=int(reports[0].attrs['flowstartseconds'])
        if newheardtime > heardtime:
            #time in local timezone, probably should use UTC
            botmessage="Alert: " + str(datetime.datetime.fromtimestamp(newheardtime).strftime('%c')) + " " + reports[0].attrs['sendercallsign'] + " " + reports[0].attrs['frequency']
            boturl="https://api.telegram.org/bot" + APIKEY + "/sendMessage?chat_id=" + CHATID + " &parse_mode=Markdown&text=" + botmessage
            print(botmessage)
            result=requests.get(boturl)
            heardtime=newheardtime

    #print out all reports
        for report in reversed(reports):
            if report.has_attr('frequency') and report.has_attr('snr'):
                print(datetime.datetime.fromtimestamp(int(report.attrs['flowstartseconds'])).strftime('%c'), 
                    report.attrs['sendercallsign'], report.attrs['receivercallsign'], report.attrs['snr'],
                    int(report.attrs['frequency'])/1000000)
    
    #don't poll quicker than every 300 seconds
    time.sleep(300)
