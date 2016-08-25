from bittorrent import Tracker
from datetime import datetime
import time
import socket
import json
import sys
import threading

def peer_info(queue,trackers):
    while True:
        print 'info:',trackers.server_class.torrents
        db = dict(trackers.server_class.torrents)
        #print db 
        db['source'] = 'tracker'
        db['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db['type'] = 'peer_info'
        queue.put(db)
        time.sleep(3)   

def transmit(queue,socket):
    while True:
        if not queue.empty():
            data = queue.get()
            try:
                datas = json.dumps(data)
                print len(datas)
                #socket.sendall(str(len(datas))+'\n'+datas)
                socket.sendall(datas+'\n')
            except:
                'Error: error during transmitting data'
           
    
tracker = Tracker()
tracker.run()
data_sending = True
if data_sending:
    ip = '192.168.144.149'
    port = 50000
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
    except:
        print 'Connection fail'
        sys.exit()
    trans = threading.Thread(target=transmit,args=(tracker.server_class.queue,sock),name='thread-transdata')
    trans.setDaemon(True)
    trans.start()

while True:
    db = dict(tracker.server_class.torrents)
    for k,v in db.iteritems():
        print len(v),
    print '' 
    if data_sending:
        hashid = []
        peers = []
        for k,v in db.iteritems():
            hashid.append(k)
            peers.append(v)
        for k in hashid:
            del db[k]
        db['hash'] = hashid
        db['peers'] = peers
        db['source'] = 'tracker'
        db['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db['type'] = 'peer_list'
        
        tracker.server_class.queue.put(db)
        #print 'info:',db
    time.sleep(3)
