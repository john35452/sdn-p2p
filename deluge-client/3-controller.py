#!/usr/bin/python

"""
This example creates a multi-controller network from semi-scratch by
using the net.add*() API and manually starting the switches and controllers.

This is the "mid-level" API, which is an alternative to the "high-level"
Topo() API which supports parametrized topology classes.

Note that one could also create a custom switch class and pass it into
the Mininet() constructor.
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController,CPULimitedHost
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import custom,pmonitor
import commands
import threading
import time
import socket
import json
import requests
import os

def transflow(left,right,sdn,socket):
    while True:
        data = {'source':'switch'}
        for k in left:
            q = commands.getoutput('sudo ovs-ofctl dump-flows '+k.name)
            q = q.split('\n')
            data[k.name] = q
        try:
            socket.sendall(json.dumps(data))
        except:
            print 'Error: error during transmitting flow'
        time.sleep(3)

def multiControllerNet():
    "Create a network from semi-scratch with multiple controllers."

    CONTROLLER_IP='192.168.144.149'
    #CONTROLLER_IP='127.0.0.1'
    #net = Mininet( controller=Controller,host=CPULimitedHost)
    net = Mininet(controller=Controller)
    print "*** Creating (reference) controllers"
    #c1 = net.addController( 'c1', port=6633)
    c1 = net.addController('c1', controller=RemoteController,ip=CONTROLLER_IP,port=6633)
    #c2 = net.addController( 'c2', port=6634 )
    c2 = net.addController('c2', controller=RemoteController,ip=CONTROLLER_IP,port=6634)
    #c3 = net.addController( 'c3', port=6635 )
    c3 = net.addController('c3', controller=RemoteController,ip=CONTROLLER_IP,port=6635)

    layer = 5
    tmp = 1<<layer
    print "*** Creating switches"
    sdn_switch = [net.addSwitch('S%d'%(n),dpid = str(n+1).zfill(16)) for n in range(1)]
    left_switch = [net.addSwitch('L%d'%(n+1),dpid = str(n+1+100).zfill(16)) for n in range(tmp-1)]
    right_switch = [net.addSwitch('R%d'%(n+tmp),dpid = str(n+1+200).zfill(16)) for n in range(tmp-1)]
    #f = open('switch_list','w')
    switch_name = [n.name for n in sdn_switch]
    #switch_name = switch_name + [n.name for n in right_switch]
    #switch_name = switch_name + [n.name for n in sdn_switch]
    with open('switch_list','w') as f:
        f.write(' '.join(switch_name)) 
    print 'Finish writing switch_list'
       
    print "*** Creating hosts"
    hosts1 = [ net.addHost( 'h%d' % (n+1) ,ip='10.0.0.%s'%(n+1),mac='00:00:00:00:00:%s'%(hex(n+1)[2:])) for n in range(tmp) ]
    hosts2 = [ net.addHost( 'h%d' % (n+1+tmp) ,ip='10.0.0.%s'%(100+n+1),mac='00:00:00:00:01:%s'%(hex(n+1)[2:])) for n in range(tmp) ]

    print "*** Creating links"
    for i in range(len(left_switch)/2):
        net.addLink(left_switch[i],left_switch[(i+1)*2-1],2,1)
        net.addLink(left_switch[i],left_switch[(i+1)*2],3,1)
    for i in range(len(right_switch)/2):
        net.addLink(right_switch[i],right_switch[(i+1)*2-1],2,1)
        net.addLink(right_switch[i],right_switch[(i+1)*2],3,1)
    for i in range(len(sdn_switch)):
        net.addLink(sdn_switch[i],left_switch[0],2,1)
        net.addLink(sdn_switch[i],right_switch[0],3,1)
  
    ''' 
    for i in range(4): 
        for j in range(2):
            net.addLink(left_switch[i+3],hosts1[2*i+j])
            net.addLink(right_switch[i+3],hosts2[2*i+j])
    '''
    tmp >>= 1
    for i in range(tmp):
        for j in range(2):
            net.addLink(left_switch[i+tmp-1],hosts1[2*i+j],2+j,1)
            net.addLink(right_switch[i+tmp-1],hosts2[2*i+j],2+j,1)
    tmp <<= 1
    print "*** Starting network"
    net.build()
    net.addNAT(ip='10.0.0.254',mac='00:00:00:00:00:FF').configDefault()
    #net.build()
    c1.start()
    c2.start()
    c3.start()
    
    for k in left_switch:
        k.start([c3])
        k.cmd('ovs-vsctl set bridge '+k.name+' protocols=OpenFlow13')
    for k in right_switch:
        k.start([c2])
        k.cmd('ovs-vsctl set bridge '+k.name+' protocols=OpenFlow13')
    for k in sdn_switch:
        k.start([c1])
        k.cmd('ovs-vsctl set bridge '+k.name+' protocols=OpenFlow13')
    print 'Finish bridges setting'
    
    ovs_url = 'http://'+CONTROLLER_IP+':8080/v1.0/conf/switches/'+str(1).zfill(16)+'/ovsdb_addr'
    queue_url = 'http://'+CONTROLLER_IP+':8080/qos/queue/status/'+str(1).zfill(16)
    rule_url = 'http://'+CONTROLLER_IP+':8080/qos/rules/'+str(1).zfill(16)
    

    #connect ovsdb
    sdn_switch[0].cmdPrint('ovs-vsctl set-manager ptcp:6632')
    payload = "tcp:"+'192.168.144.134'+":6632"
    response = requests.put(ovs_url,data=json.dumps(payload))
    print response,response.text
    #c1.cmdPrint('curl -X PUT -d \'"tcp:127.0.0.1:6632"\' http://localhost:8080/v1.0/conf/switches/0000000000000001/ovsdb_addr') 
    
    #local queue setting
    times = tmp**2+tmp+1
    print 'Add ',times,'queues to S0-eth2 and S0-eth3'
    q1 = []
    q2 = []
    for i in range(times):
        q1.append(str(i)+'=@q'+str(i))
        q2.append('-- --id=@q'+str(i)+' create Queue other-config:max-rate='+str(1000*1000*8))
    q1 = ','.join(q1)
    q2 = ' '.join(q2)
    CMD = 'ovs-vsctl'
    sdn_switch[0].cmd(CMD+' -- set Port S0-eth2 qos=@newqos -- --id=@newqos create Qos type=linux-htb other-config:max-rate=1000000000 queues='+q1+' '+q2)
    sdn_switch[0].cmd(CMD+' -- set Port S0-eth3 qos=@newqos -- --id=@newqos create Qos type=linux-htb other-config:max-rate=1000000000 queues='+q1+' '+q2)
    '''
    times = tmp<<1+1
    print 'Add ',times,'queues to S0-eth4'
    q1 = []
    q2 = []
    for i in range(times):
        q1.append(str(i)+'=@q'+str(i))
        q2.append('-- --id=@q'+str(i)+' create Queue other-config:max-rate=1000000000')
    q1 = ','.join(q1)
    q2 = ' '.join(q2)
    sdn_switch[0].cmd(CMD+' -- set Port S0-eth4 qos=@newqos -- --id=@newqos create Qos type=linux-htb other-config:max-rate=100000000 queues='+q1+' '+q2)
    '''

    '''
    time.sleep(1) 
    #queue setting using request, but it only afford about 500 queue

    #payload = {"port_name":"S0-eth2","type":"linux-htb","max_rate":"10000000","queues":[{"max_rate":"1000000"},{"min_rate":"500000"}]}
    unlimit_speed = {'max_rate':'1000000000'}
    payload = {"type": "linux-htb", "queues": [unlimit_speed]*(2)}
    payloads = json.dumps(payload)
    print len(payloads)
    t1 = time.time()
    try:
        response = requests.post(url,data=payloads)
    except:
        print 'timeout'
    print time.time()-t1
    print response
    print 'Queue estabish'
    #Queue setting using curl, but it only afford about 1500 queue 
    #If you want to use curl, the item in the dictionary must like "a":"1". But str(payload) looks like 'a':'1', so it won't work.
    #However, the output of json.dumps is appropriate for this
    #c1.cmdPrint("curl -X POST -d '"+json.dumps(payload)+"' "+url)
    '''
    print 'Add matching flow'
    source_provider = '192.168.144.149'
    for i in range(tmp):
        for j in range(tmp):
            payload = {'match':{'nw_src':'10.0.0.%s'%(i+1),'nw_dst':'10.0.0.%s'%(100+j+1),'nw_proto':'UDP'},'actions':{'queue':str(i*tmp+j+1)}}
            response = requests.post(rule_url,data=json.dumps(payload))
            if response.status_code!=200:
                print response,response.text
            payload = {'match':{'nw_src':'10.0.0.%s'%(i+1+100),'nw_dst':'10.0.0.%s'%(j+1),'nw_proto':'UDP'},'actions':{'queue':str(i*tmp+j+1)}}
            response = requests.post(rule_url,data=json.dumps(payload))
            if response.status_code!=200:
                print response,response.text
            
    for i in range(tmp):
        payload = {'match':{'nw_src':source_provider,'nw_dst':'10.0.0.%s'%(i+1),'nw_proto':'UDP'},'actions':{'queue':str(tmp*tmp+i+1)}}
        response = requests.post(rule_url,data=json.dumps(payload))
        if response.status_code!=200:
            print response,response.text
        payload = {'match':{'nw_src':source_provider,'nw_dst':'10.0.0.%s'%(i+1+100),'nw_proto':'UDP'},'actions':{'queue':str(tmp*tmp+i+1)}}
        response = requests.post(rule_url,data=json.dumps(payload))
        if response.status_code!=200:
            print response,response.text
    print 'Finish adding flow'    
    
    for k in sdn_switch: 
        for i in range(tmp):
            print i,'round'
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,udp,ip_src='+source_provider+',ip_dst=10.0.0.%s,action=output:2'%(i+1))
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,tcp,ip_src='+source_provider+',ip_dst=10.0.0.%s,action=output:2'%(i+1))
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=1,eth_type=2048,ip_src='+source_provider+',ip_dst=10.0.0.%s,action=output:2'%(i+1))
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,udp,ip_src='+source_provider+',ip_dst=10.0.0.%s,action=output:3'%(i+1+100))
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,tcp,ip_src='+source_provider+',ip_dst=10.0.0.%s,action=output:3'%(i+1+100))
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=1,eth_type=2048,ip_src='+source_provider+',ip_dst=10.0.0.%s,action=output:3'%(i+1+100))
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,udp,ip_src=10.0.0.%s,ip_dst='%(i+1)+source_provider+',action=output:4')
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,tcp,ip_src=10.0.0.%s,ip_dst='%(i+1)+source_provider+',action=output:4')
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=1,eth_type=2048,ip_src=10.0.0.%s,ip_src='%(i+1)+source_provider+',action=output:4')
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,udp,ip_src=10.0.0.%s,ip_dst='%(i+1+100)+source_provider+',action=output:4')
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,tcp,ip_src=10.0.0.%s,ip_dst='%(i+1+100)+source_provider+',action=output:4')
            k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=1,eth_type=2048,ip_src=10.0.0.%s,ip_src='%(i+1+100)+source_provider+',action=output:4')
            
            for j in range(tmp):
                k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,udp,ip_src=10.0.0.%s,ip_dst=10.0.0.%s,action=output:2'%(j+1+100,i+1))
                k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,tcp,ip_src=10.0.0.%s,ip_dst=10.0.0.%s,action=output:2'%(j+1+100,i+1))
                k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=1,eth_type=2048,ip_src=10.0.0.%s,ip_dst=10.0.0.%s,action=output:2'%(j+1+100,i+1))
                k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,udp,ip_src=10.0.0.%s,ip_dst=10.0.0.%s,action=output:3'%(j+1,i+1+100))
                k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=2,tcp,ip_src=10.0.0.%s,ip_dst=10.0.0.%s,action=output:3'%(j+1,i+1+100))
                k.cmd('ovs-ofctl -O OpenFlow13 add-flow '+k.name+' table=1,priority=1,eth_type=2048,ip_src=10.0.0.%s,ip_dst=10.0.0.%s,action=output:3'%(j+1,i+1+100))
    
    '''
    for i in range(tmp<<1):
        sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=2,udp,ip_dst=10.0.0.%s,action=output:2'%(i+1))
        sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=2,tcp,ip_dst=10.0.0.%s,action=output:2'%(i+1))
        #sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=2,eth_type=2054,ip_dst=10.0.0.%s,action=output:2'%(i+1))
        sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=1,eth_type=2048,ip_dst=10.0.0.%s,action=output:2'%(i+1))
        sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=2,udp,ip_dst=10.0.0.%s,action=output:3'%(100+i+1))
        sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=2,tcp,ip_dst=10.0.0.%s,action=output:3'%(100+i+1))
        #sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=2,eth_type=2054,ip_dst=10.0.0.%s,action=output:3'%(100+i+1))  
        sdn_switch[0].cmdPrint('ovs-ofctl -O OpenFlow13 add-flow S15 priority=1,eth_type=2048,ip_dst=10.0.0.%s,action=output:3'%(100+i+1))
    '''
    print "*** Testing network"
    #net.pingAll()
     
    popens = {}
    for i in range(tmp):
        print 'activate',i
        #popens[hosts1[i]] = hosts1[i].popen('python client.py 1 1 %s user1 > %s &'%(i,'user1'+str(i)))
        #popens[hosts2[i]] = hosts2[i].popen('python client.py 1 2 %s user1 > %s &'%(i,'user2'+str(i)))
        hosts1[i].cmd('nohup python client.py 1 1 %s 200s/4/user1%s > %s &'%(i,str(i+1).zfill(2),'user1'+str(i+1).zfill(2)+'.txt'))
        #time.sleep(1)
        hosts2[i].cmd('nohup python client.py 1 2 %s 200s/4/user2%s > %s &'%(i,str(i+1).zfill(2),'user2'+str(i+1).zfill(2)+'.txt'))
        #time.sleep(1)
    
        #hosts1[i].cmd('nohup python client.py 1 1 %s test3/user1%s > %s &'%(i,i,'user1'+str(i)+'.txt'))
        #hosts2[i].cmd('nohup python client.py 1 2 %s test3/user2%s > %s &'%(i,i,'user2'+str(i)+'.txt'))
    
    '''
    for host,line in pmonitor(popens):
        if host:
            print "<%s>: %s" % ( host.name, line.strip() )
    '''
    '''
    print 'host1'
    hosts1[0].cmd('python client.py 1 1 1 user1 > a &')
    print 'host2'
    hosts1[1].cmd('python client.py 1 1 2 user1 > b &')
    print "*** Running CLI"
    '''
    CLI( net )
    print "*** Stopping network"
    net.stop()
    print 'destroy qos setting'
    os.system('ovs-vsctl --all destroy qos')
    os.system('ovs-vsctl --all destroy queue')
    print 'stop ovsdb manager'
    os.system('ovs-vsctl del-manager')
if __name__ == '__main__':
    setLogLevel( 'info' )  # for CLI output
    multiControllerNet()
