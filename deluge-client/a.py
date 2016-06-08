from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import os

def emptyNet():

    NODE2_IP='192.168.144.134'
    CONTROLLER_IP='192.168.144.126'

    net = Mininet( topo=None,
                   build=False)

    #c0 = net.addController( 'c0',controller=RemoteController,ip=CONTROLLER_IP,port=6633)
    net.addController('c0', port=6633)

    h1 = net.addHost( 'h1', ip='10.0.0.1' )
    h2 = net.addHost( 'h2', ip='10.0.0.2' )
    s1 = net.addSwitch( 's1' )
    net.addLink( h1, s1,1,1)
    net.addLink( h2, s1,1,2)
    net.build()
    net.addNAT(ip='10.0.0.5').configDefault()
    net.start()
    #net.addNAT().configDefault()
    #s1.start([c0])
    #s1.cmdPrint('ovs-vsctl set bridge s1 protocols=OpenFlow13')
    # Configure the GRE tunnel
    s1.cmdPrint('ovs-vsctl add-port s1 s1-gre1 -- set interface s1-gre1 type=gre ofport_request=5 options:remote_ip='+NODE2_IP)
    s1.cmdPrint('ovs-vsctl show')
    #s1.cmdPrint('ovs-vsctl set bridge s1 protocols=OpenFlow13')
    #os.system('ovs-ofctl add-flow s1 eth_type=2048,ip_dst=10.0.1.3,action=output:5')
    #os.system('ovs-ofctl add-flow s1 eth_type=2048,ip_dst=10.0.1.4,action=output:5')
    #os.system('ovs-ofctl add-flow s1 eth_type=2054,ip_dst=10.0.1.3,action=output:5')
    #os.system('ovs-ofctl add-flow s1 eth_type=2054,ip_dst=10.0.1.4,action=output:5')
    h1.cmdPrint('ip link set mtu 1454 dev h1-eth1')
    h2.cmdPrint('ip link set mtu 1454 dev h2-eth1')
    nat = net.get('nat0')
    nat.cmdPrint('ip link set mtu 1454 dev nat0-eth0')
    #net.addNAT().configDefault()
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
