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

    h3 = net.addHost( 'h3', ip='10.0.0.3' )
    h4 = net.addHost( 'h4', ip='10.0.0.4' )
    s2 = net.addSwitch( 's2' )
    net.addLink( h3, s2 )
    net.addLink( h4, s2 )
    net.start()

    # Configure the GRE tunnel
    s2.cmd('ovs-vsctl add-port s2 s2-gre1 -- set interface s2-gre1 type=gre options:remote_ip='+NODE1_IP)
    s2.cmdPrint('ovs-vsctl show')
    
    natIP='10.0.0.5'
    h3.setDefaultRoute('via %s'% natIP)
    h4.setDefaultRoute('via %s'% natIP)
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    emptyNet()
