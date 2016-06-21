import os
import SocketServer
import time
import json
from datetime import datetime

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
	print datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data = self.request.recv(2048).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        self.request.sendall('Receive '+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        result = json.loads(self.data)
        





if __name__ == "__main__":
    HOST, PORT = '192.168.144.134',50000

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
    
    while True:
        s = raw_input('stop?')
        if s=='stop':
            server.shutdown()
            server.server_close()
            break
    '''
    left_number = right_number = 32
    #left_base = '10.0.0.'
    #right_base = '10.0.0.1'
    
    times = left_number*right_number+(left_number+right_number)+1
    speed_record = [1000000000]*times
    print 'Add ',times,'queues to S0-eth2 and S0-eth3'
    q1 = []
    q2 = []
    for i in range(times):
        q1.append(str(i)+'=@q'+str(i))
        q2.append('-- --id=@q'+str(i)+' create Queue other-config:max-rate='+str(speed_record[i]))
    q1 = ','.join(q1)
    q2 = ' '.join(q2)
    CMD = 'ovs-vsctl'
    sdn_switch[0].cmd(CMD+' -- set Port S0-eth2 qos=@newqos -- --id=@newqos create Qos type=linux-htb other-config:max-rate=1000000000 queues='+q1+' '+q2)
    sdn_switch[0].cmd(CMD+' -- set Port S0-eth3 qos=@newqos -- --id=@newqos create Qos type=linux-htb other-config:max-rate=1000000000 queues='+q1+' '+q2)
    '''

