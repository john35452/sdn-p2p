from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost,Controller,RemoteController,OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
import os

class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        # Initialize topology and default options
                Topo.__init__(self, **opts)
                # Add your logic here ...
                cs_switch = self.addSwitch('s1')
                for i in range(fanout):
                    as_switch = self.addSwitch('A%d'% ((i+1)+1))
                    #self.addLink(cs_switch,as_switch,**linkopts1)
                    self.addLink(cs_switch,as_switch)
                    for j in range(fanout):
                        es_switch = self.addSwitch('E%d'%(2*(i+1)+2+j))
                        #self.addLink(as_switch,es_switch,**linkopts3)
                        self.addLink(as_switch,es_switch)
                        for k in range(fanout):
                            host = self.addHost('h%d'%(2*(2*(i+1)+2+j)+k))
                            #self.addLink(host,es_switch,**linkopts3)
                            self.addLink(host,es_switch)  

#Function used to "test/verify" your topo
def perfTest():
   "Create network and run simple performance test"
   #"--- core to aggregation switches"
   linkopts1 = {'bw':50, 'delay':'5ms'}
   #"--- aggregation to edge switches"
   linkopts2 = {'bw':30, 'delay':'10ms'}
   #"--- edge switches to hosts"
   linkopts3 = {'bw':10, 'delay':'15ms'}
   topo = CustomTopo(linkopts1 , linkopts2 , linkopts3 , fanout= 2)
   #net = Mininet(topo=topo,host=CPULimitedHost, link=TCLink)
   net = Mininet(controller=None,topo=topo)
   c = net.addController('c0',controller=RemoteController,ip='127.0.0.1',port=6633)
   #net.addNAT().configDefault()
   #net.build()
   #c.start()
   net.start()
   net.startTerms()
   '''
   os.popen('ovs-vsctl add-port s1 eth0')
   for i in range(8,16):
       h = net.get('h%d'%(i))
       h.cmdPrint('dhclient '+h.defaultIntf().name)
   CLI(net)
   for i in range(8,16):
       h = net.get('h%d'%(i))
       h.cmdPrint('dhclient -r '+h.defaultIntf().name)
   net.stop()
   '''
   h = net.get('h9')
   h.cmd('ifconfig')
   CLI(net)
   net.stop()

topos = { 'custom': ( lambda: CustomTopo() ) }

#Main function used to conduct the test
if __name__ == "__main__":
 setLogLevel('info')
 perfTest()

