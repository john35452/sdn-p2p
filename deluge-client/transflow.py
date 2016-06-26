import commands
import time
import socket
import json
import sys
import re
from datetime import datetime
import traceback

ip = '192.168.144.149'
port = 50000
try:
    f = open('switch_list','r')
except:
    print "switch_list doesn't exist"
    sys.exit()

switch_list = f.readline()
switch_list = switch_list.split()
print switch_list

print 'Establish connection'
while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        break
    except:
        print 'Connection fail'
        time.sleep(1)

while True:
    data = {'source':'switch','timestamp':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    for k in switch_list:
        q = commands.getoutput('sudo ovs-ofctl -O OpenFlow13 dump-flows '+k)
        q = q.replace(',',' ')
        q = filter(lambda x:not x.startswith('OFPST_FLOW'),q.split('\n')[1:])
        data[k] = []
        for i in q:
            tmp = {}
            i = i.strip()
            i = re.split(' +',i)
            for j in i:
                j = j.split('=')
                if len(j)<2:
                    if 'type' not in tmp:
                        tmp['type']=j[0]
                    else:
                        j = j[0].split(':')
                        try:
                            tmp[j[0]] = j[1]
                        except:
                            print j
                            sys.exit()
                else:
                    tmp[j[0]] = j[1]
            data[k].append(tmp)
        #print data[k]
    try:
        #print 'data:',data
        datas = json.dumps(data)
        size = len(datas)
        print 'size:',size
        #sock.sendall(str(size)+'\n'+datas)
        sock.sendall(datas+'\n')
    except Exception:
        traceback.print_exc()
        print 'Error: error during transmitting flow'
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        print 'Re-establish connection and send data'
        sock.sendall(datas+'\n') 
    time.sleep(3)
