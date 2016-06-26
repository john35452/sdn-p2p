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
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier

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
                        print 'total memory:',asizeof.asizeof(data[i]),'total len:',len(data[i])
                        datas = json.loads(data[i])
                        datas['ip'] = self.client_address[0]
                        datas['port'] = self.client_address[1]
                        #print sys.getsizeof(datas)
                        write_queue.put(datas)
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

class prediction(threading.Thread):
    def __init__(self,queue):
        super(prediction,self).__init__()
        self.queue = queue
        self.flow = []
        self.period = 60
        self.timer = time.time()
        self.ip = ('192.168.144.134',50000)
        self.feature = ['host_name','host_count','all_in_number','connectivity','all_in_bytes','all_in_packets','udp_in_number','udp_in_bytes','udp_in_packets','udp_in_speed','udp_in_packet_size','udp_in_percentage','tcp_in_number','tcp_in_bytes','tcp_in_packets','tcp_in_speed','ip_in_number','ip_in_bytes','ip_in_packets','ip_in_speed','all_out_number','all_out_bytes','all_out_packets','udp_out_number','udp_out_bytes','udp_out_packets','udp_out_speed','udp_out_packet_size','udp_out_percentage','tcp_out_number','tcp_out_bytes','tcp_out_packets','tcp_out_speed','ip_out_number','ip_out_bytes','ip_out_packets','ip_out_speed']
        
        try:
            self.model = joblib.load('./model/RF_c.pkl') 
            print 'Load model successfully'   
        except:
            traceback.print_exc()    
            print 'Fail to read machine learning model'

    def run(self):
        while not start:
            pass
        self.timer = time.time()
        print '**************************start downloading*******************************************'
        while not terminate:            
            while not self.queue.empty():
                data = self.queue.get()
                self.flow.append(data)
            if time.time()-self.timer>self.period:
                print '***************************************************Prediction*********************************************************'
                self.timer = time.time()
                '''
                if len(self.flow)<20:
                    continue
                if float(self.flow[-1]['S0'][0]['duration'][:-1])<self.period:
                    print '**************************too fast*******************************************'
                    print self.flow[-1]['S0'][0]['duration']
                    continue
                '''
                output = {}
                host = {}
                tmp = 32
                source_provider = '192.168.144.149'
                for i in range(tmp):
                    host['10.0.0.%s'%(i+1)] = {'peer_ids':[],'hash':[],'port':[],'torrent':{},'in':{'udp':{},'tcp':{},'ip':{},'other':{}},'out':{'udp':{},'tcp':{},'ip':{},'other':{}}}
                    host['10.0.0.%s'%(i+1+100)] = {'peer_ids':[],'hash':[],'port':[],'torrent':{},'in':{'udp':{},'tcp':{},'ip':{},'other':{}},'out':{'udp':{},'tcp':{},'ip':{},'other':{}}}
                host[source_provider] = {'peer_ids':[],'hash':[],'port':[],'torrent':{},'in':{'udp':{},'tcp':{},'ip':{},'other':{}},'out':{'udp':{},'tcp':{},'ip':{},'other':{}}}
                for k in host.keys():
                    output[k] = {'host_name':k,'host_count':tmp*2}
                sdn_switch_list = ['S0']
                for k in self.flow:
                    for rule in k['S0']:
                        #print rule['n_bytes'],rule['table']
                        if rule['n_bytes']=='0' or rule['table']=='0':
                            continue
                        if 'nw_dst' in rule and 'nw_src' in rule:
                            #in
                            if rule['nw_src'] not in host[rule['nw_dst']]['in'][rule['type']]:
                                host[rule['nw_dst']]['in'][rule['type']][rule['nw_src']] = [{'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1])}]
                            else:
                                host[rule['nw_dst']]['in'][rule['type']][rule['nw_src']].append({'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1])})
                            #out
                            if rule['nw_dst'] not in host[rule['nw_src']]['out'][rule['type']]:
                                host[rule['nw_src']]['out'][rule['type']][rule['nw_dst']] = [{'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1])}]
                            else:
                                host[rule['nw_src']]['out'][rule['type']][rule['nw_dst']].append({'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1])})
                print '***********************************Read flow***********************************************'
                direction = ['in','out']
                flow_type = ['udp','tcp','ip']
                test_x = []
                host_list = host.keys()
                for k in host_list:
                    all_peer = []
                    for direct in direction:
                        #print direct
                        peer = []
                        for _type in flow_type:
                            output[k][_type+'_'+direct+'_number'] = len(host[k][direct][_type])
                            byte = 0.0
                            packet = 0.0
                            speed = 0.0
                            ignore_speed = 0
                            for a,b in host[k][direct][_type].iteritems():
                                if a not in peer:
                                    peer.append(a)
                                byte += b[-1]['n_bytes'] - b[0]['n_bytes']
                                packet += b[-1]['n_packets'] - b[0]['n_packets']
                                if len(b)==1:
                                    ignore_speed += 1
                                    continue
                                times = 0.0
                                for j in range(len(b)-1):
                                    if b[j+1]['n_bytes']>b[j]['n_bytes']:
                                        times += b[j+1]['duration'] - b[j]['duration']
                                if times>0: 
                                    speed += (b[-1]['n_bytes']-b[0]['n_bytes'])/times
                            output[k][_type+'_'+direct+'_bytes'] = byte
                            output[k][_type+'_'+direct+'_packets'] = packet
                            output[k][_type+'_'+direct+'_speed'] = speed/output[k][_type+'_'+direct+'_number'] if output[k][_type+'_'+direct+'_number']>0 else 0.0
                            if _type == 'udp':
                                output[k]['udp_'+direct+'_packet_size'] = byte/packet if packet>0 else 0.0
                        output[k]['all_'+direct+'_bytes'] = 0
                        output[k]['all_'+direct+'_packets'] = 0
                        output[k]['all_'+direct+'_number'] = len(peer)
                        all_peer = all_peer + [n for n in peer if n not in all_peer]
                        for _type in flow_type:
                            output[k]['all_'+direct+'_bytes'] += output[k][_type+'_'+direct+'_bytes']
                            output[k]['all_'+direct+'_packets'] += output[k][_type+'_'+direct+'_packets']
                        output[k]['udp_'+direct+'_percentage'] = float(output[k]['udp_'+direct+'_packets'])/output[k]['all_'+direct+'_packets'] if output[k]['all_'+direct+'_packets'] > 0 else 0.0
                    output[k]['connectivity'] = float(len(all_peer))/output[k]['host_count']
                    test_x.append([output[k][n] for n in self.feature[1:]])
                print '***********************************Machine learning result***********************************************'
                test_y = self.model.predict(test_x)
                result = {}
                for k in range(len(host_list)):
                    result[host_list[k]]=test_y[k] 
                self.flow = []
                client(self.ip[0],self.ip[1],json.dumps(result))
                

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
        print 'Send prediction successfully'
    except:
        print 'Error during tranmitting prediction'
    finally:
        sock.close()
        

def writefile(queue,flow_queue):
    global start
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
    start_list = []
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
                    if not start:
                        if data['inter_ip'][0] not in start_list:
                            start_list.append(data['inter_ip'][0])
                            if len(start_list)==64:
                                start = True
            elif data['source']=='switch':
                f4.writerow(data)
                if start and punishment:
                    flow_queue.put(data)
        elif terminate:
            break

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    #HOST, PORT = "localhost", 50000
    HOST, PORT = '192.168.144.149', 50000
   
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print 'Server: ip:',ip,'PORT:',port
    print threading.activeCount()
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    terminate = False
    punishment = False
    start = False
    write_queue = Queue.Queue()
    flow_queue = Queue.Queue()
    server_thread = threading.Thread(target=server.serve_forever)
    write_thread = threading.Thread(target=writefile,args=(write_queue, flow_queue),name='thread-writefile')
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    write_thread.setDaemon(True)
    server_thread.start()
    write_thread.start()
    if punishment:
        prediction_thread = prediction(flow_queue)
        prediction_thread.setDaemon(True)
        prediction_thread.start()
    print "Server loop running in thread:", server_thread.name
    while True:
        data = raw_input('request\n')
        print threading.activeCount()
        if data=='stop':
            terminate = True
            server.shutdown()
            server.server_close()
            write_thread.join()
            break
