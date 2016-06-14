import socket
import threading
import SocketServer
import json
import sys
import Queue
import time
import csv
import traceback
from pympler import asizeof

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        '''
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = "{} ip:{}: {}".format(cur_thread.name, self.client_address,data)
        self.request.sendall(response)
        '''
        cur_thread = threading.current_thread()
        server.a.append(cur_thread)
        print server.a
        print 'Thread:',cur_thread,'address:',self.client_address
        long_data = ''
        while True:
            try:
                try:
                    data = self.request.recv(1024)
                except:
                    print 'Receiving error'
                data = data.split('\n')
                partition = len(data)
                for i in range(partition):
                    if i<partition-1:
                        if long_data!='':
                            data[i] = long_data+data[i]
                            long_data = ''
                        print 'total memory:',asizeof.asizeof(data[i])
                        print 'total len:',len(data[i])
                        datas = json.loads(data[i])
                        datas['ip'] = self.client_address[0]
                        datas['port'] = self.client_address[1]
                        #print sys.getsizeof(datas)
                        server.queue.put(datas)
                        response = "{} ip:{}: {}".format(cur_thread.name,self.client_address,sys.getsizeof(datas))
                        self.request.sendall(response)
                    else:                           
                        if data[i]=='':
                            continue
                        else:
                            long_data += data[i]
            except Exception:
                #print data
                traceback.print_exc()    
                print 'Thread terminate:',cur_thread
                server.a.remove(cur_thread)
                break
        '''
        data = self.request.recv(102400)
        datas = json.loads(data)
        print datas
        while True:
            data = self.request.recv(1024)
            if data =='':
                print 'Thread terminate:',cur_thread
                server.a.remove(cur_thread)
                break
            response = "{} ip:{}: {}".format(cur_thread.name, self.client_address,data)
            self.request.sendall(response)
        '''
          
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    a = []
    queue = Queue.Queue()
    terminate = False

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

def writefile(queue):
    standard = ['source','ip','port','timestamp']
    tracker_list1 = ['type','hash','peers']
    tracker_list2 = ['type','inter_ip','uploaded','compact','numwant','no_peer_id','info_hash','event','downloaded','redundant','key','corrupt','peer_id','supportcrypto','left']
    switch_list = open('switch_list','r').read().split()
    client_list = ['inter_ip','hash','content'] 
    f1 = csv.DictWriter(open('data_client.csv','w'),standard+client_list)
    f2 = csv.DictWriter(open('data_tracker_peer.csv','w'),standard+tracker_list1)
    f3 = csv.DictWriter(open('data_tracker_request.csv','w'),standard+tracker_list2)
    f4 = csv.DictWriter(open('data_switch.csv','w'),standard+switch_list)
    f1.writeheader()
    f2.writeheader()
    f3.writeheader()
    f4.writeheader()
    while True:
        if not queue.empty():
            data = queue.get()
            if data['source']=='client':
                f1.writerow(data)
            elif data['source']=='tracker':
                if data['type']=='peer_list':
                    f2.writerow(data)    
                else:
                    f3.writerow(data)
            elif data['source']=='switch':
                f4.writerow(data)
        elif server.terminate:
            break

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    #HOST, PORT = "localhost", 50000
    HOST, PORT = '192.168.144.124', 50000
   
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print 'Server: ip:',ip,'PORT:',port
    print threading.activeCount()
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    write_thread = threading.Thread(target=writefile,args=(server.queue, ),name='thread-writefile')

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    write_thread.setDaemon(True)
    server_thread.start()
    write_thread.start()
    print "Server loop running in thread:", server_thread.name
    while True:
        data = raw_input('request\n')
        print threading.activeCount()
        if data=='stop':
            server.terminate = True
            server.shutdown()
            server.server_close()
            write_thread.join()
            break
