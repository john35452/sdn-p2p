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
from datetime import datetime,timedelta
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
                        #print 'total memory:',asizeof.asizeof(data[i]),'total len:',len(data[i])
                        print 'total len:',len(data[i])
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
    def __init__(self,queue1,queue2,queue3):
        super(prediction,self).__init__()
        self.flow_queue = queue1
        self.tracker_queue = queue2
        self.user_queue = queue3
        self.flow = []
        self.event = []
        self.user = []
        self.period = 200
        self.timer = time.time()
        self.start_time = datetime.now()
        self.ip = ('192.168.144.134',50000)
        #self.feature = ['host_name','all_in_number','all_in_bytes','all_in_packets','udp_in_number','udp_in_bytes','udp_in_packets','udp_in_speed','udp_in_packet_size','udp_in_percentage','tcp_in_number','tcp_in_bytes','tcp_in_packets','tcp_in_speed','ip_in_number','ip_in_bytes','ip_in_packets','ip_in_speed','all_out_number','all_out_bytes','all_out_packets','udp_out_number','udp_out_bytes','udp_out_packets','udp_out_speed','udp_out_packet_size','udp_out_percentage','tcp_out_number','tcp_out_bytes','tcp_out_packets','tcp_out_speed','ip_out_number','ip_out_bytes','ip_out_packets','ip_out_speed']
        self.feature = ['host_name','all_in_number','all_in_bytes','all_in_packets','udp_in_number','udp_in_bytes','udp_in_packets','udp_in_speed','udp_in_packet_size','udp_in_percentage','tcp_in_number','tcp_in_bytes','tcp_in_packets','tcp_in_speed','ip_in_number','ip_in_bytes','ip_in_packets','ip_in_speed','all_out_number','all_out_bytes','all_out_packets','udp_out_number','udp_out_bytes','udp_out_packets','udp_out_speed','udp_out_packet_size','udp_out_percentage','tcp_out_number','tcp_out_bytes','tcp_out_packets','tcp_out_speed','ip_out_number','ip_out_bytes','ip_out_packets','ip_out_speed','start_count','stop_count','middle_count','task_count','average_download','average_upload','active_percentage','seeding_percentage','average_payload_download_speed','average_payload_upload_speed','average_upload_speed_limit','num_peers','max_connection']

        try:
            self.model = joblib.load('./model/RF_c.pkl') 
            print 'Load model successfully'   
        except:
            traceback.print_exc()    
            print 'Fail to read machine learning model'

    def run(self):
        while not start:
            pass
        while not self.tracker_queue.empty():
            data = self.tracker_queue.get()
            if data['inter_ip'][0].startswith('10.0.'):
                data['timestamp'] = datetime.strptime(data['timestamp'],'%Y-%m-%d %H:%M:%S')
                self.event.append(data)
        self.start_time = min(filter(lambda x:x['event'][0]=='started',self.event),key=lambda x:x['timestamp'])['timestamp']
        print '***************************Start time:',self.start_time
        self.event = filter(lambda x:x['timestamp']>=self.start_time,self.event)
        while not self.flow_queue.empty():
            data = self.flow_queue.get()
            data['timestamp'] = datetime.strptime(data['timestamp'],'%Y-%m-%d %H:%M:%S')
            if data['timestamp']>=self.start_time:
                self.flow.append(data)
        while not self.user_queue.empty():
            data = self.user_queue.get()
            data['timestamp'] = datetime.strptime(data['timestamp'],'%Y-%m-%d %H:%M:%S')
            if data['timestamp']>=self.start_time:
                self.user.append(data)
        self.timer = time.time()
        print '**************************start downloading*******************************************'
        while not terminate:            
            while not self.flow_queue.empty():
                data = self.flow_queue.get()
                data['timestamp'] = datetime.strptime(data['timestamp'],'%Y-%m-%d %H:%M:%S')
                self.flow.append(data)
            while not self.tracker_queue.empty():
                data = self.tracker_queue.get()
                data['timestamp'] = datetime.strptime(data['timestamp'],'%Y-%m-%d %H:%M:%S')
                self.event.append(data)
            while not self.user_queue.empty():
                data = self.user_queue.get()
                data['timestamp'] = datetime.strptime(data['timestamp'],'%Y-%m-%d %H:%M:%S')
                self.user.append(data)
            if time.time()-self.timer>=self.period:
                print '***************************************************Prediction*********************************************************'
                self.timer = time.time()
                tmp_flow = filter(lambda x:self.start_time<=x['timestamp'] and x['timestamp']<self.start_time+timedelta(seconds=self.period),self.flow)
                tmp_event = filter(lambda x:self.start_time<=x['timestamp'] and x['timestamp']<self.start_time+timedelta(seconds=self.period),self.event)
                tmp_user = filter(lambda x:self.start_time<=x['timestamp'] and x['timestamp']<self.start_time+timedelta(seconds=self.period),self.user)
                output = {}
                host = {}
                rate = {}
                rate2 = {}
                average_speed = {}
                tmp = 32
                source_provider = '192.168.144.149'
                for i in range(tmp):
                    host['10.0.0.%s'%(i+1)] = {'peer_ids':[],'hash':[],'port':[],'torrent':{},'in':{'udp':{},'tcp':{},'ip':{},'other':{}},'out':{'udp':{},'tcp':{},'ip':{},'other':{}}}
                    host['10.0.0.%s'%(i+1+100)] = {'peer_ids':[],'hash':[],'port':[],'torrent':{},'in':{'udp':{},'tcp':{},'ip':{},'other':{}},'out':{'udp':{},'tcp':{},'ip':{},'other':{}}}
                host[source_provider] = {'peer_ids':[],'hash':[],'port':[],'torrent':{},'in':{'udp':{},'tcp':{},'ip':{},'other':{}},'out':{'udp':{},'tcp':{},'ip':{},'other':{}}}
                for k in host.keys():
                    #output[k] = {'host_name':k,'host_count':tmp*2}
                    output[k] = {'host_name':k}
                sdn_switch_list = ['S0']
                for k in tmp_flow:
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
                direction = ['in','out']
                flow_type = ['udp','tcp','ip']
                test_x = []
                host_list = [ n for n in host.keys() if n.startswith('10.0')]
                for k in host_list:
                    #Get feature from flow
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
                            output[k][_type+'_'+direct+'_speed'] = speed/(output[k][_type+'_'+direct+'_number']-ignore_speed) if (output[k][_type+'_'+direct+'_number']-ignore_speed)>0 else 0.0
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
                    #output[k]['connectivity'] = float(len(all_peer))/output[k]['host_count']
                    #Get feature from tracker event
                    start_count = 0
                    stop_count = 0
                    middle_count = 0
                    task = []
                    for hashid in host[k]['hash']:
                        for j in host[k]['torrent'][hashid]['started']:
                            start_count += 1
                            if hashid not in task:
                                task.append(hashid)    
                        for j in host[k]['torrent'][hashid]['stopped']:
                            stop_count += 1   
                            if hashid not in task:
                                task.append(hashid)    
                        for j in host[k]['torrent'][hashid]['middle']:
                            middle_count += 1    
                            if hashid not in task:
                                task.append(hashid)
                    output[k]['start_count'] = start_count
                    output[k]['stop_count'] = stop_count
                    output[k]['middle_count'] = middle_count
                    output[k]['task_count'] = len(task)
                    output[k]['average_download'] = output[k]['udp_in_bytes']/(3*(self.period))
                    output[k]['average_upload'] = output[k]['udp_out_bytes']/(3*(self.period))
                    #get output from user_data
                    client_tmp = filter(lambda x:x['inter_ip'][0]==k,tmp_user)
                    if len(client_tmp)==0:
                        print 'Length of client_tmp is zero:',k
                    _start = {}
                    for j in range(len(client_tmp)):
                        if len(_start)==len(client_tmp[-1]['hash']):
                            break
                        for _hash in client_tmp[j]['hash']:
                            if _hash not in _start:
                                _start[_hash] = j
                    total_time = 0.0
                    active_time = 0.0
                    seed_time = 0.0
                    payload_download = 0.0
                    payload_upload = 0.0
                    payload_download2 = 0.0
                    payload_upload2 = 0.0
                    #download_limit = 0.0
                    upload_limit = 0.0
                    max_peer = 0
                    max_connection = 0
                    active_time2 = 0.0
                    for j in range(len(client_tmp[-1]['hash'])):
                        payload_download2 += client_tmp[-1]['content'][j]['total_payload_download']
                        payload_upload2 += client_tmp[-1]['content'][j]['total_payload_upload']
                        start_index = client_tmp[_start[client_tmp[-1]['hash'][j]]]['hash'].index(client_tmp[-1]['hash'][j])
                        active_time += (client_tmp[-1]['content'][j]['active_time']-client_tmp[_start[client_tmp[-1]['hash'][j]]]['content'][start_index]['active_time'])     
                        active_time2 += (client_tmp[-1]['timestamp']-client_tmp[_start[client_tmp[-1]['hash'][j]]]['timestamp']).seconds     
                        seed_time += (client_tmp[-1]['content'][j]['seeding_time']-client_tmp[_start[client_tmp[-1]['hash'][j]]]['content'][start_index]['seeding_time'])     
                        payload_download += (client_tmp[-1]['content'][j]['total_payload_download']-client_tmp[_start[client_tmp[-1]['hash'][j]]]['content'][start_index]['total_payload_download'])     
                        payload_upload += (client_tmp[-1]['content'][j]['total_payload_upload']-client_tmp[_start[client_tmp[-1]['hash'][j]]]['content'][start_index]['total_payload_upload'])   
                        total_time += (client_tmp[-1]['timestamp']-client_tmp[_start[client_tmp[-1]['hash'][j]]]['timestamp']).seconds
                    for j in range(len(client_tmp)-1):
                        for m in range(len(client_tmp[j]['hash'])):
                            #download_limit += client_tmp[j]['content'][m]['max_download_speed']*(client_tmp[j+1]['timestamp']-client_tmp[j]['timestamp']).seconds
                            upload_limit += client_tmp[j]['content'][m]['max_upload_speed']*(client_tmp[j+1]['timestamp']-client_tmp[j]['timestamp']).seconds
                            if client_tmp[j]['content'][m]['num_peers']>max_peer:
                                max_peer = client_tmp[j]['content'][m]['num_peers']
                            if client_tmp[j]['content'][m]['max_connections']>max_connection:
                                max_connection = client_tmp[j]['content'][m]['max_connections']
                    for m in client_tmp[-1]['content']:
                        if m['num_peers']>max_peer:
                            max_peer = m['num_peers']
                        if m['max_connections']>max_connection:
                            max_connection = m['max_connections']
                    #if active_time!= active_time2:
                    #    print k,active_time,active_time2
                    output[k]['active_percentage'] = active_time2/total_time
                    output[k]['seeding_percentage'] = seed_time/total_time
                    output[k]['average_payload_download_speed'] = payload_download/active_time
                    output[k]['average_payload_upload_speed'] = payload_upload/active_time 
                    #output[k]['average_download_speed_limit'] = download_limit/total_time 
                    output[k]['average_upload_speed_limit'] = upload_limit/total_time
                    output[k]['num_peers'] = max_peer
                    output[k]['max_connection'] = max_connection
                    rate[k] = payload_download/payload_upload if payload_upload>0 else 999
                    rate2[k] = payload_download2/payload_upload2 if payload_upload2>0 else 999
                    average_speed[k] = output[k]['average_payload_download_speed']
                    test_x.append([output[k][n] for n in self.feature[1:]])
                    
                print '***********************************Machine learning result***********************************************'
                test_y = self.model.predict(test_x)
                result = {}
                for k in range(len(host_list)):
                    result[host_list[k]]=test_y[k]
                data = [result,rate,rate2,average_speed]
                self.flow = [n for n in self.flow if n not in tmp_flow]
                self.event = [n for n in self.event if n not in tmp_event]
                self.user = [n for n in self.user if n not in tmp_user]
                self.start_time = self.start_time + timedelta(seconds=self.period)
                client(self.ip[0],self.ip[1],json.dumps(data))
                print 'It takes %lf seconds'%(time.time()-self.timer)
                

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message+'\n')
        response = sock.recv(1024)
        print "Received: {}".format(response)
        print 'Send prediction successfully'
    except:
        print 'Error during tranmitting prediction'
    finally:
        sock.close()
        

def writefile(queue,flow,tracker,user):
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
                user.put(data)
            elif data['source']=='tracker':
                if data['type']=='peer_list':
                    f2.writerow(data)    
                else:
                    f3.writerow(data)
                    tracker.put(data)
                    if not start:
                        if data['inter_ip'][0] not in start_list:
                            start_list.append(data['inter_ip'][0])
                            if len(start_list)==64:
                                start = True
            elif data['source']=='switch':
                f4.writerow(data)
                flow.put(data)
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
    punishment = True
    start = False
    write_queue = Queue.Queue()
    flow_queue = Queue.Queue()
    tracker_queue = Queue.Queue()
    user_queue = Queue.Queue()
    server_thread = threading.Thread(target=server.serve_forever)
    write_thread = threading.Thread(target=writefile,args=(write_queue, flow_queue,tracker_queue,user_queue),name='thread-writefile')
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    write_thread.setDaemon(True)
    server_thread.start()
    write_thread.start()
    if punishment:
        prediction_thread = prediction(flow_queue,tracker_queue,user_queue)
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
