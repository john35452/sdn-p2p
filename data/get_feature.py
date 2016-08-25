import sys
import time
import csv
from datetime import datetime,timedelta
try:
    fin1 = open(sys.argv[1]+'data_client.csv','r')
    fin2 = open(sys.argv[1]+'data_switch.csv','r')
    fin3 = open(sys.argv[1]+'data_tracker_peer.csv','r')
    fin4 = open(sys.argv[1]+'data_tracker_request.csv','r')
    fin5 = open(sys.argv[1]+'answer.csv','r')
except:
    print 'data missing'
    sys.exit()

t1 = time.time()
data_client = []
data_switch = []
data_tracker_peer = []
data_tracker_request = []
csv.field_size_limit(sys.maxsize)
print 'Read data_client'

reader = csv.DictReader(fin1)
for row in reader:
    data_client.append(row)
for row in data_client:
    row['inter_ip'] = tuple(eval(row['inter_ip']))
    row['timestamp'] = datetime.strptime(row['timestamp'],'%Y-%m-%d %H:%M:%S')
    row['hash'] = eval(row['hash'])
    row['content'] = eval(row['content'])

    
t2 = time.time()
print 'It takes %lf seconds to read data_client'%(t2-t1)

print 'Read data_switch'
reader = csv.DictReader(fin2)
for row in reader:
    data_switch.append(row)
for row in data_switch:
    row['S0'] = eval(row['S0'])
    row['timestamp'] = datetime.strptime(row['timestamp'],'%Y-%m-%d %H:%M:%S')
t3 = time.time()
print 'It takes %lf seconds to read data_switch'%(t3-t2)

print 'Read data_tracker_peer'
reader = csv.DictReader(fin3)
for row in reader:
    data_tracker_peer.append(row)
for row in data_tracker_peer:
    row['hash'] = eval(row['hash'])
    row['peers'] = eval(row['peers'])
    row['timestamp'] = datetime.strptime(row['timestamp'],'%Y-%m-%d %H:%M:%S')
t4 = time.time()
print 'It takes %lf seconds to read tracker_peer'%(t4-t3)

count = {}
print 'Read data_tracker_request'
reader = csv.DictReader(fin4)
for row in reader:
    data_tracker_request.append(row)
direct = ['uploaded','compact','numwant','no_peer_id','event','downloaded','redundant','key','corrupt','peer_id','supportcrypto','left']
for row in data_tracker_request:
    for k in direct:
        if row[k]:
            row[k] = eval(row[k])[0]
    row['ip'] = str(row['ip'])
    row['port'] = int(row['port'])
    row['inter_ip'] = tuple(eval(row['inter_ip']))
    row['timestamp'] = datetime.strptime(row['timestamp'],'%Y-%m-%d %H:%M:%S')
    if row['inter_ip'][0] not in count:
        count[row['inter_ip'][0]] = 1
    else:
        count[row['inter_ip'][0]] += 1
        
t5 = time.time()
print 'It takes %lf seconds to read tracker_request'%(t5-t4)

print 'len:',len(data_client),len(data_switch),len(data_tracker_peer),len(data_tracker_request)
t6 = time.time()
print 'It takes %lf seconds to load data'%(t6-t1)

stop = 0
host = {}
for k in data_tracker_request:
    #Divided by ip
    if k['inter_ip'][0] not in host:
        host[k['inter_ip'][0]] = {'peer_ids':[],'hash':[],'port':[],'torrent':{},'in':{'udp':{},'tcp':{},'ip':{},'other':{}},'out':{'udp':{},'tcp':{},'ip':{},'other':{}}}
    if k['info_hash'] not in host[k['inter_ip'][0]]['hash']:
        host[k['inter_ip'][0]]['hash'].append(k['info_hash'])
        host[k['inter_ip'][0]]['torrent'][k['info_hash']]={'started':[],'stopped':[],'middle':[],'completed':[]}
    #torrent event time
    if k['event'] == 'started':
        host[k['inter_ip'][0]]['torrent'][k['info_hash']]['started'].append({'timestamp':k['timestamp'],'left':k['left'],'uploaded':k['uploaded'],'downloaded':k['downloaded']})
    elif k['event'] == 'stopped':
        host[k['inter_ip'][0]]['torrent'][k['info_hash']]['stopped'].append({'timestamp':k['timestamp'],'left':k['left'],'uploaded':k['uploaded'],'downloaded':k['downloaded']})
        stop += 1
    elif k['event'] == 'completed':
        #print 'complete',k['inter_ip']
        host[k['inter_ip'][0]]['torrent'][k['info_hash']]['completed'].append({'timestamp':k['timestamp'],'left':k['left'],'uploaded':k['uploaded'],'downloaded':k['downloaded']})
    else:
        host[k['inter_ip'][0]]['torrent'][k['info_hash']]['middle'].append({'timestamp':k['timestamp'],'left':k['left'],'uploaded':k['uploaded'],'downloaded':k['downloaded']})        
    #peer_id
    if k['peer_id'] not in host[k['inter_ip'][0]]['peer_ids']:
        host[k['inter_ip'][0]]['peer_ids'].append(k['peer_id'])
    #port
    #Noted that every request uses different port
    if k['inter_ip'][1] not in host[k['inter_ip'][0]]['port']:
        host[k['inter_ip'][0]]['port'].append(k['inter_ip'][1])


sdn_switch_list = ['S0']
for k in data_switch:
    for rule in k['S0']:
        #print rule['n_bytes'],rule['table']
        if rule['n_bytes']=='0' or rule['table']=='0':
            continue
        if 'nw_dst' in rule and 'nw_src' in rule:
            #in
            if rule['nw_src'] not in host[rule['nw_dst']]['in'][rule['type']]:
                host[rule['nw_dst']]['in'][rule['type']][rule['nw_src']] = [{'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1]),'timestamp':k['timestamp']}]
            else:
                host[rule['nw_dst']]['in'][rule['type']][rule['nw_src']].append({'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1]),'timestamp':k['timestamp']})
            #out
            if rule['nw_dst'] not in host[rule['nw_src']]['out'][rule['type']]:
                host[rule['nw_src']]['out'][rule['type']][rule['nw_dst']] = [{'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1]),'timestamp':k['timestamp']}]
            else:
                host[rule['nw_src']]['out'][rule['type']][rule['nw_dst']].append({'n_packets':int(rule['n_packets']),'n_bytes':int(rule['n_bytes']),'duration':float(rule['duration'][:-1]),'timestamp':k['timestamp']})

'''
#get starttime using flow
start_time_udp = []
start_time_tcp = []
start_time_ip = []
end_time_udp = []
end_time_tcp = []
end_time_ip = []
for k in host.keys():
    for v in host[k]['in']['udp'].keys():
        start_time_udp.append((k,v,'udp',host[k]['in']['udp'][v][0]['duration'],host[k]['in']['udp'][v][0]['timestamp']))
        end_time_udp.append((k,v,'udp',host[k]['in']['udp'][v][-1]['duration'],host[k]['in']['udp'][v][-1]['timestamp']))
    for v in host[k]['in']['tcp'].keys():
        start_time_tcp.append((k,v,'tcp',host[k]['in']['tcp'][v][0]['duration'],host[k]['in']['tcp'][v][0]['timestamp']))
        end_time_tcp.append((k,v,'tcp',host[k]['in']['tcp'][v][-1]['duration'],host[k]['in']['tcp'][v][-1]['timestamp']))
    for v in host[k]['in']['ip'].keys():
        start_time_ip.append((k,v,'ip',host[k]['in']['ip'][v][0]['duration'],host[k]['in']['ip'][v][0]['timestamp']))
        end_time_ip.append((k,v,'ip',host[k]['in']['ip'][v][-1]['duration'],host[k]['in']['ip'][v][-1]['timestamp']))

start_udp = min(start_time_udp,key=lambda x:x[3])
start_tcp = min(start_time_tcp,key=lambda x:x[3])
start_ip = min(start_time_ip,key=lambda x:x[3])

end_udp = max(end_time_udp,key=lambda x:x[3])
end_tcp = max(end_time_tcp,key=lambda x:x[3])
end_ip  = max(end_time_ip,key=lambda x:x[3])
print 'udp Min:',min(start_time_udp,key=lambda x:x[3])
print 'udp Min:',max(start_time_udp,key=lambda x:x[3])
print 'tcp Min:',min(start_time_tcp,key=lambda x:x[3])
print 'tcp Min:',max(start_time_tcp,key=lambda x:x[3])
print 'ip Min:',min(start_time_ip,key=lambda x:x[3])
print 'ip Min:',max(start_time_ip,key=lambda x:x[3])

print 'udp Max:',max(end_time_udp,key=lambda x:x[3])
print 'udp Max:',min(end_time_udp,key=lambda x:x[3])
print 'tcp Max:',max(end_time_tcp,key=lambda x:x[3])
print 'tcp Max:',min(end_time_tcp,key=lambda x:x[3])
print 'ip Max:',max(end_time_ip,key=lambda x:x[3])
print 'ip Max:',min(end_time_ip,key=lambda x:x[3])
'''
#get starting and ending time using tracker event
first = []
last = []
for k in host.keys():
    tmp = []
    tmp2 = []
    if k.startswith('10.0.'):
        for v in host[k]['hash']:
            #print k,v,host[k]['torrent'][v]['stopped']
            tmp.append(host[k]['torrent'][v]['started'][0]['timestamp'])
            if len(host[k]['torrent'][v]['stopped'])>0:
                tmp2.append(host[k]['torrent'][v]['stopped'][0]['timestamp'])
        first.append(min(tmp))
        if len(tmp2)>0:
            last.append(max(tmp2))

print 'First:',min(first),max(first)
print 'Last:',min(last),max(last)
print 'Time:',max(last)-min(first),min(first)+timedelta(seconds=1000),max(first)+timedelta(seconds=1000)

time_period = [min(first)]
period = 200
for i in range(((max(last)-min(first)).seconds)/period-1):
    time_period.append(time_period[-1]+timedelta(seconds=period))
time_period.append(max(last))
print time_period
#print 'start_time:',start_time_udp
#print 'end_time:',end_time


#Make Output file
data_list = ['host_name','all_in_number','all_in_bytes','all_in_packets','udp_in_number','udp_in_bytes','udp_in_packets','udp_in_speed','udp_in_packet_size','udp_in_percentage','tcp_in_number','tcp_in_bytes','tcp_in_packets','tcp_in_speed','ip_in_number','ip_in_bytes','ip_in_packets','ip_in_speed','all_out_number','all_out_bytes','all_out_packets','udp_out_number','udp_out_bytes','udp_out_packets','udp_out_speed','udp_out_packet_size','udp_out_percentage','tcp_out_number','tcp_out_bytes','tcp_out_packets','tcp_out_speed','ip_out_number','ip_out_bytes','ip_out_packets','ip_out_speed','start_count','stop_count','middle_count','task_count','average_download','average_upload','active_percentage','seeding_percentage','average_payload_download_speed','average_payload_upload_speed','average_upload_speed_limit','num_peers','max_connection']
direction = ['in','out']
flow_type = ['udp','tcp','ip']
y = {}

for i in range(len(time_period)-1):
    output = {}
    for k in host.keys():
        if k.startswith('10.0.'):
            #output[k] = {'host_name':k,'host_count':len(host.keys())}
            output[k] = {'host_name':k}
    fout = open(sys.argv[1]+'train_x_'+str(i+1)+'.csv','w')
    fout2 = open(sys.argv[1]+'train_y_'+str(i+1)+'.csv','w')
    writer = csv.DictWriter(fout,data_list)
    writer.writeheader()
    #Get output from tracker and flow
    for k in host.keys():
        if not k.startswith('10.0.'):
            continue
        all_peer = []
        for direct in direction:
            #print direct
            direct_peer = []
            for _type in flow_type:
                peer = []
                byte = 0.0
                packet = 0.0
                speed = 0.0
                ignore_speed = 0
                for a,b in host[k][direct][_type].iteritems():
                    tmp_flow = filter(lambda x:time_period[i]<=x['timestamp'] and x['timestamp']<time_period[i+1],b)
                    if len(tmp_flow)==0:
                        continue
                    else:
                        peer.append(a)
                    byte += tmp_flow[-1]['n_bytes'] - tmp_flow[0]['n_bytes']
                    packet += tmp_flow[-1]['n_packets'] - tmp_flow[0]['n_packets']
                    times = 0.0
                    if len(tmp_flow)==1:
                        ignore_speed += 1
                        continue 
                    for j in range(len(tmp_flow)-1):
                        if tmp_flow[j+1]['n_bytes']>tmp_flow[j]['n_bytes']:
                            times += (tmp_flow[j+1]['timestamp'] - tmp_flow[j]['timestamp']).seconds
                        elif tmp_flow[j+1]['n_bytes']<tmp_flow[j]['n_bytes']:
                            print 'something fuck happens that counter went wrong'
                    if times>0:
                        speed += byte/times 
                all_peer = all_peer + [n for n in peer if n not in all_peer]
                direct_peer = direct_peer + [n for n in peer if n not in direct_peer]
                
                output[k][_type+'_'+direct+'_number'] = len(peer)
                output[k][_type+'_'+direct+'_bytes'] = byte
                output[k][_type+'_'+direct+'_packets'] = packet
                output[k][_type+'_'+direct+'_speed'] = speed/(output[k][_type+'_'+direct+'_number']-ignore_speed) if (output[k][_type+'_'+direct+'_number']-ignore_speed)>0 else 0.0
                if _type == 'udp':
                    output[k]['udp_'+direct+'_packet_size'] = byte/packet if packet>0 else 0.0                
            output[k]['all_'+direct+'_bytes'] = 0
            output[k]['all_'+direct+'_packets'] = 0
            output[k]['all_'+direct+'_number'] = len(direct_peer)
            for _type in flow_type:
                output[k]['all_'+direct+'_bytes'] += output[k][_type+'_'+direct+'_bytes']
                output[k]['all_'+direct+'_packets'] += output[k][_type+'_'+direct+'_packets']
            output[k]['udp_'+direct+'_percentage'] = float(output[k]['udp_'+direct+'_packets'])/output[k]['all_'+direct+'_packets'] if output[k]['all_'+direct+'_packets'] > 0 else 0.0 
            #print k,direct,peer
        #output[k]['connectivity'] = float(len(all_peer))/output[k]['host_count']
        #Get feature from tracker event
        start_count = 0
        stop_count = 0
        middle_count = 0
        task = []
        for hashid in host[k]['hash']:
            for j in host[k]['torrent'][hashid]['started']:
                if time_period[i]<=j['timestamp'] and j['timestamp']<time_period[i+1]:
                    start_count += 1
                    if hashid not in task:
                        task.append(hashid)    
            for j in host[k]['torrent'][hashid]['stopped']:
                if time_period[i]<=j['timestamp'] and j['timestamp']<time_period[i+1]:
                    stop_count += 1   
                    if hashid not in task:
                        task.append(hashid)    
            for j in host[k]['torrent'][hashid]['middle']:
                if time_period[i]<=j['timestamp'] and j['timestamp']<time_period[i+1]:
                    middle_count += 1    
                    if hashid not in task:
                        task.append(hashid) 
         
        output[k]['start_count'] = start_count
        output[k]['stop_count'] = stop_count
        output[k]['middle_count'] = middle_count
        output[k]['task_count'] = len(task)
        output[k]['average_download'] = output[k]['udp_in_bytes']/(3*((time_period[i+1]-time_period[i]).seconds))
        output[k]['average_upload'] = output[k]['udp_out_bytes']/(3*((time_period[i+1]-time_period[i]).seconds))

        #get output from user_data
        client_tmp = filter(lambda x:x['inter_ip'][0]==k and time_period[i]<=x['timestamp'] and x['timestamp']<=time_period[i+1],data_client)
        _start = {}
        for j in range(len(client_tmp)):
            if len(_start)==3:
                break
            for _hash in client_tmp[j]['hash']:
                if _hash not in _start:
                    _start[_hash] = j
        total_time = 0.0
        active_time = 0.0
        seed_time = 0.0
        payload_download = 0.0
        payload_upload = 0.0
        #download_limit = 0.0
        upload_limit = 0.0
        max_peer = 0
        max_connection = 0
        active_time2 = 0.0
        for j in range(len(client_tmp[-1]['hash'])):
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
        for j in client_tmp:
            if len(j['content'])>0:
                print j['content'][0]['total_peers']
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
        category = [1,2,5,float('inf')]
        rank = 0
        rate = payload_download/payload_upload if payload_upload>0 else 999
        for m in range(len(category)):
            if category[m]>rate:
                rank = m
                break
        y[k] = [rate,rank]
        #print k
        #print 'active_time:',active_time,'total_time',total_time
        #print 'payload_upload:',payload_upload
    print 'finish parsing ',(i+1),'period flow' 

    print 'Writing output file'
    for k in host.keys():
        if k.startswith('10.0'):
            writer.writerow(output[k])
            fout2.write(k+','+str(y[k][0])+','+str(y[k][1])+'\n')
    fout.close()
    fout2.close()
print '%lf seconds'%(time.time()-t6)
'''   
for k,v in host.iteritems():
    #print k,len(v['hash']),len(v['port']),len(v['peer_ids']),count[k]
    print k,len(v['torrent'])
    for a,b in v['torrent'].iteritems():
        print len(b['started']),len(b['stopped']),len(b['middle']),len(b['completed'])
    #        if len(c)==0:
    #            print 'no start'
    #            print k,a
'''            
#for k,v in host.iteritems():
    #print k,v
