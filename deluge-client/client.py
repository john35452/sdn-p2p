from p2p_client import p2p_client
import sys
import time
import socket
import json
import threading
import os
from datetime import datetime

def transmit_data(client,socket):
    while True:
        threadlock.acquire()
        status = client.get_torrents_status()
        threadlock.release()
        #print status
        hashid = []
        content = []
        for k,v in status.iteritems():
            hashid.append(k)
            content.append(v)
        for k in hashid:
            del status[k]
        status['hash'] = hashid
        status['content'] = content
        status['source'] = 'client'
        status['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            data = json.dumps(status)
            #socket.sendall(str(len(data))+'\n'+data+'\n')
            socket.sendall(data+'\n')
        except:
            print 'Error: error during transmitting data'
        time.sleep(3)

print sys.argv     
if len(sys.argv)<4:
    print 'Usage: python client.py [new_daemon] [com_id] [host_id] ([process file])'
    sys.exit()
elif len(sys.argv)>4:
    process_file = sys.argv[4]
else:
    process_file = ''
#print process_file
a = p2p_client(sys.argv[2],sys.argv[3])
if sys.argv[1]=='1':
    a.config()
    a.start_daemon()
a.get_user_info()
a.login()
state = a.get_session_state()
print state
torrent_file = {}
#Transmit to server
data_sending = True
if data_sending:
    ip = '192.168.144.124'
    port = 50000
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            break
        except:
            print 'Connection fail'

    threadlock = threading.Lock()
    trans = threading.Thread(target=transmit_data,args=(a,sock),name='thread-transdata')
    trans.setDaemon(True)
    trans.start()

if process_file=='':
    while True:
        command = raw_input('command:\n1.get_session_state 2.clean_session 3.add_torrent 4.remove_torrent 5.create_torrent 6.pause_torrent 7.resume_torrent 8.torrent_status 9.limit_download_speed 10.shutdown\n')
        #command = command.split()
        #print command
        if command == '1':
            print a.get_session_state()
        elif command == '2':
            a.clean_session()
        elif command == '3':
            torrent = os.listdir('./experiment/torrent')
            print 'torrent list:'
            for i in range(len(torrent)):
                print i,torrent[i],' ',
            print ''
            number = raw_input('number of torrent')
            a.add_torrent(torrent[int(number)])
        elif command == '4':
            torrent = a.get_session_state()
            a.remove_torrent(torrent[0])
        elif command == '5':
            a.create_torrent('240MB.txt','240MB','john')
        elif command == '6':
            torrent = a.get_session_state()
            a.pause_torrent(torrent)
        elif command == '7':
            torrent = a.get_session_state()
            a.resume_torrent(torrent)
        elif command == '8':
            number = raw_input('number of torrent')
            torrent = a.get_session_state()
            data = a.get_torrent_status(torrent[int(number)])
            data = sorted(data.iteritems())
            for k in data:
                print k
        elif command == '9':
            speed = raw_input('Limit speed to?')
            torrent = a.get_session_state()
            a.set_torrent_max_download_speed(torrent[0],float(speed))
        elif command == '10':
            a.shutdown()
            break
else:
    with open('./experiment/action/'+process_file,'r') as fin:
        t1 = time.time()
        for line in fin:
            line = line.split()
            if line[0] == '1':
                #might not use
                threadlock.acquire()
                print a.get_session_state()
                threadlock.release()
            elif line[0] == '2':
                print 'clean session'
                threadlock.acquire()
                a.clean_session()
                threadlock.release()
            elif line[0] == '3':
                print 'add torrent:',line[1]
                threadlock.acquire()
                a.add_torrent(line[1])
                data = a.get_torrents_status()
                threadlock.release()
                for k,v in data.iteritems():
                    if v['name']+'.torrent' not in torrent_file:
                        torrent_file[v['name']+'.torrent'] = k
                print torrent_file
            elif line[0] == '4':
                threadlock.acquire()
                #torrent = a.get_session_state()
                #a.remove_torrent(torrent[int(line[1])])
                a.remove_torrent(torrent_file[line[1]])
                threadlock.release()
                print 'remove torrent: name:',line[1],'hash:',torrent_file[line[1]]
            elif line[0] == '5':
                print 'create_torrent:',line[1]
                threadlock.acquire()
                a.create_torrent(line[1],line[1],'john')
                data = a.get_torrents_status()
                threadlock.release()
                for k,v in data.iteritems():
                    if v['name']+'.torrent' not in torrent_file:
                        torrent_file[v['name']+'.torrent'] = k
                print torrent_file
            elif line[0] == '6':
                print 'pause torrent:',line[1:]
                threadlock.acquire()
                a.pause_torrent([torrent_file[n] for n in line[1:]])
                threadlock.release()
            elif line[0] == '7':
                print 'resume torrent:',line[1:]
                threadlock.acquire()
                a.resume_torrent([torrent_file[n] for n in line[1:]])
                threadlock.release()
            elif line[0] == '8':
                #might not use
                number = raw_input('number of torrent')
                torrent = a.get_session_state()
                data = a.get_torrent_status(torrent[int(number)])
                data = sorted(data.iteritems())
                for k in data:
                    print k
            elif line[0] == 'ds':
                print 'limit download torrent %s to %s KB per second'%(line[1],line[2])
                threadlock.acquire()
                a.set_torrent_max_download_speed(torrent_file[line[1]],float(line[2]))
                threadlock.release()
            elif line[0] == 'us':
                print 'limit upload torrent %s to %s KB per second'%(line[1],line[2])
                threadlock.acquire()
                a.set_torrent_max_upload_speed(torrent_file[line[1]],float(line[2]))
                threadlock.release()
            elif line[0] == '10':
                print 'Task finishes'
                threadlock.acquire()
                a.shutdown()
                threadlock.release()
                break
            elif line[0] == 'sf':
                print 'get session status'
                key = ['has_incoming_connections','download_rate','upload_rate','total_download','tracker_upload_rate','total_tracker_download','total_redundant_bytes','num_peers','num_unchoked','down_bandwidth_queue','unchoke_counter','utp_stats']
                threadlock.acquire()
                data = a.get_session_status(key)
                threadlock.release()
                result = sorted(data.iteritems())
                for k in result:
                    print k
            elif line[0] == 'f':
                threadlock.acquire()
                data = a.get_torrent_status(torrent_file[line[1]])
                threadlock.release()
                print 'torrent at %s finish:%s\nIntegrity:%s/%s %s Average speed:%lf\nDownload:%s Upload:%s'%(line[1],data['is_finished'],data['total_payload_download'],data['total_wanted'],data['progress'],data['total_payload_download']/(30*1024),data['total_payload_download'],data['total_payload_upload'])
            elif line[0] == 's':
                print 'sleep for',line[1],'seconds'
                time.sleep(int(line[1]))
    print 'It takes %lf seconds totally'%(time.time()-t1)
