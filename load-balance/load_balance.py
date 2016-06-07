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
import time
import os

def multiControllerNet():
    "Create a network from semi-scratch with multiple controllers."

    #net = Mininet( controller=Controller,host=CPULimitedHost)
    net = Mininet(controller=Controller)
    print "*** Creating (reference) controllers"
    c1 = net.addController( 'c1', port=6633 )
    #c1 = net.addController('c1', controller=RemoteController,ip='127.0.0.1',port=6633)
    #c2 = net.addController( 'c2', port=6634 )
    #c2 = net.addController('c2', controller=RemoteController,ip='127.0.0.1',port=6634)
    #c3 = net.addController( 'c3', port=6635 )
    #c3 = net.addController('c3', controller=RemoteController,ip='127.0.0.1',port=6635)

    print "*** Creating switches"
    sdn_switch = [net.addSwitch('S%d'%(n)) for n in range(3,6)]
    left_switch = [net.addSwitch('L%d'%(n)) for n in range(1,2)]
    right_switch = [net.addSwitch('R%d'%(n)) for n in range(2,3)]
    #f = open('switch_list','w')
    switch_name = [n.name for n in left_switch]
    switch_name = switch_name + [n.name for n in right_switch]
    switch_name = switch_name + [n.name for n in sdn_switch]
    with open('switch_list','w') as f:
        f.write(' '.join(switch_name)) 
    print 'Finish writing switch_list'
       
    print "*** Creating hosts"
    hosts1 = [ net.addHost( 'h%d' % (n+1) ,ip='10.0.0.1') for n in range(1) ]
    hosts2 = [ net.addHost( 'h%d' % (n+2) ,ip='10.0.0.2') for n in range(1) ]

    print "*** Creating links"
    net.addLink(hosts1[0],left_switch[0],1,1)
    net.addLink(hosts2[0],right_switch[0],1,1)
    for k in range(len(sdn_switch[:-1])):
        net.addLink(left_switch[0],sdn_switch[k],2+k,1)
        net.addLink(right_switch[0],sdn_switch[k],2+k,2)
 

    print "*** Starting network"
    #net.staticArp()
    net.build()
    #net.addNAT().configDefault()
    #nat = net.addNAT(connect=None)
    #net.addLink(nat,sdn_switch[0])
    #nat.configDefault()
    #net.build()
    #net.staticArp()
    c1.start()
    #c2.start()
    #c3.start()
    for k in left_switch:
        k.start([c1])
        k.cmd('ovs-vsctl set bridge '+k.name+' protocols=OpenFlow13')
        #k.cmd('ovs-vsctl set bridge '+k.name+' stp_enable=true')
    for k in right_switch:
        k.start([c1])
        k.cmd('ovs-vsctl set bridge '+k.name+' protocols=OpenFlow13')
        #k.cmd('ovs-vsctl set bridge '+k.name+'stp_enable=true')
    for k in sdn_switch:
        k.start([c1])
        k.cmd('ovs-vsctl set bridge '+k.name+' protocols=OpenFlow13')
        #k.cmd('ovs-vsctl set bridge '+k.name+'stp_enable=true')
 
    os.system('ovs-ofctl -O OpenFlow13 add-group L1 group_id=1,type=select,bucket=output:2,bucket=output:3')
    os.system('ovs-ofctl -O OpenFlow13 add-group R2 group_id=2,type=select,bucket=weight:4,output:2,bucket=weight:6,output:3')
    os.system('ovs-ofctl -O OpenFlow13 add-flow L1 in_port=1,action=group:1')
    os.system('ovs-ofctl -O OpenFlow13 add-flow R2 in_port=1,action=group:2')
    os.system('ovs-ofctl -O OpenFlow13 add-flow L1 eth_type=2048,ip_dst=10.0.0.1,action=output:1')
    os.system('ovs-ofctl -O OpenFlow13 add-flow L1 eth_type=2054,ip_dst=10.0.0.1,action=output:1')
    os.system('ovs-ofctl -O OpenFlow13 add-flow R2 eth_type=2048,ip_dst=10.0.0.2,action=output:1')
    os.system('ovs-ofctl -O OpenFlow13 add-flow R2 eth_type=2054,ip_dst=10.0.0.2,action=output:1')
    os.system('ovs-ofctl -O OpenFlow13 add-flow S3 in_port=1,actions=output:2')
    os.system('ovs-ofctl -O OpenFlow13 add-flow S3 in_port=2,actions=output:1')
    os.system('ovs-ofctl -O OpenFlow13 add-flow S4 in_port=1,actions=output:2')
    os.system('ovs-ofctl -O OpenFlow13 add-flow S4 in_port=2,actions=output:1')

    print "*** Testing network"
    #net.pingAll()
    '''
    popens = {}
    for i in range(tmp<<1):
        print 'activate',i
        #popens[hosts1[i]] = hosts1[i].popen('python client.py 1 1 %s user1 > %s &'%(i,'user1'+str(i)))
        #popens[hosts2[i]] = hosts2[i].popen('python client.py 1 2 %s user1 > %s &'%(i,'user2'+str(i)))
        hosts1[i].cmd('python client.py 1 1 %s user1 > %s &'%(i,'user1'+str(i)))
        hosts2[i].cmd('python client.py 1 2 %s user1 > %s &'%(i,'user2'+str(i)))
   
    for host,line in pmonitor(popens):
        if host:
            print "<%s>: %s" % ( host.name, line.strip() )
    '''
    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )  # for CLI output
    multiControllerNet()
