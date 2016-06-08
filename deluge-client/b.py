from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def emptyNet():

    NODE1_IP='192.168.144.126'
    CONTROLLER_IP='192.168.144.126'

    net = Mininet( topo=None,
                   build=False)

    net.addController( 'c0',
                      controller=RemoteController,
                      ip=CONTROLLER_IP,
                      port=6633)

    h3 = net.addHost( 'h3', ip='10.0.1.3' )
    h4 = net.addHost( 'h4', ip='10.0.1.4' )
    s2 = net.addSwitch( 's2' )
    net.addLink( h3, s2 ,1,1)
    net.addLink( h4, s2 ,1,2)
    net.start()

    #s2.cmdPrint('ovs-vsctl set bridge s2 protocols=OpenFlow13')
    # Configure the GRE tunnel
    s2.cmdPrint('ovs-vsctl add-port s2 s2-gre1 -- set interface s2-gre1 type=gre ofport_request=5 options:remote_ip='+NODE1_IP)
    h3.cmdPrint('ip link set mtu 1454 dev h3-eth1')
    h4.cmdPrint('ip link set mtu 1454 dev h4-eth1')
    #s2.cmdPrint('ovs-vsctl set bridge s2 protocols=OpenFlow13')
    s2.cmdPrint('ovs-vsctl show')
    #s2.cmdPrint('ovs-ofctl add-flow s2 eth_type=2048,ip_dst=10.0.1.3,action=output:1')    
    #s2.cmdPrint('ovs-ofctl add-flow s2 eth_type=2048,ip_dst=10.0.1.4,action=output:2')
    #s2.cmdPrint('ovs-ofctl add-flow s2 eth_type=2054,ip_dst=10.0.1.3,action=output:1')
    #s2.cmdPrint('ovs-ofctl add-flow s2 eth_type=2054,ip_dst=10.0.1.4,action=output:2')

 
    natIP='10.0.0.5'
    h3.setDefaultRoute('via %s'% natIP)
    h4.setDefaultRoute('via %s'% natIP)
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
