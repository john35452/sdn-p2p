import os
import SocketServer
import time
import json
import csv
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
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        #modify_speed(result)
        
def modify_speed(data):
    global speed_record_right,speed_record_left
    for i in range(left_number):
        if data[left_base+'%s'%(i+1)] == 0:
            speed = speed_record_left[i+1] + 100*1000*8
            if speed>1000*1000*8:
                speed = 1000*1000*8
            data[left_base+str(i+1)+'_speed'] = speed
            for j in range(right_number):
                speed_record_left[i+left_number*j+1] = speed
            speed_record_left[right_number*left_number+i+1] = speed
                
        elif data[left_base+'%s'%(i+1)] == 1:
            data[left_base+str(i+1)+'_speed'] = speed_record_left[i+1]
            #for j in range(left_number):
            #    speed_record[i*left_number+j+1] = speed_record[i*left_number+j+1]+100 if speed_record[i*left_number+j+1]<1000 else 1000
        elif data[left_base+'%s'%(i+1)] == 2:
            speed = speed_record_left[i+1] - 50*1000*8
            if speed<100*1000*8:
                speed = 100*1000*8
            data[left_base+str(i+1)+'_speed'] = speed
            for j in range(right_number):
                speed_record_left[i+left_number*j+1] = speed
        elif data[left_base+'%s'%(i+1)] == 3:
            speed = speed_record_left[i+1] - 100*1000*8
            if speed<100*1000*8:
                speed = 100*1000*8
            data[left_base+str(i+1)+'_speed'] = speed
            for j in range(right_number):
                speed_record_left[i+left_number*j+1] = speed
    
    for i in range(right_number):
        if data[right_base+'%s'%(i+1+100)] == 0:
            speed = speed_record_right[i+1] + 100*1000*8
            if speed >1000*1000*8:
                speed = 1000*1000*8
            data[right_base+str(i+1+100)+'_speed'] = speed
            for j in range(left_number):
                speed_record_right[i+j*right_number+1] = speed
            speed_record_right[right_number*left_number+i+1] = speed
        elif data[right_base+'%s'%(i+1+100)] == 1:
            data[right_base+str(i+1+100)+'_speed'] = speed_record_right[i+1]
            #for j in range(left_number):
            #    speed_record[i*left_number+j+1] = speed_record[i*left_number+j+1]+100 if speed_record[i*left_number+j+1]<1000 else 1000
        elif data[right_base+'%s'%(i+1+100)] == 2:
            speed = speed_record_right[i+1] - 50*1000*8
            if speed <100*1000*8:
                speed = 100*1000*8
            data[right_base+str(i+1+100)+'_speed'] = speed
            for j in range(left_number):
                speed_record_right[i+j*right_number+1] = speed
           
        elif data[right_base+'%s'%(i+1+100)] == 3:
            speed = speed_record_right[i+1] - 100*1000*8
            if speed <100*1000*8:
                speed = 100*1000*8
            data[right_base+str(i+1+100)+'_speed'] = speed
            for j in range(left_number):
                speed_record_right[i+j*right_number+1] = speed
    
    print 'Change S0-eth2 speed'
    q1 = []
    q2 = []
    for i in range(times+left_number):
        q1.append(str(i)+'=@q'+str(i))
        q2.append('-- --id=@q'+str(i)+' create Queue other-config:max-rate='+str(speed_record_right[i]))
    q1 = ','.join(q1)
    q2 = ' '.join(q2)
    CMD = 'ovs-vsctl'
    os.system(CMD+' -- set Port S0-eth2 qos=@newqos -- --id=@newqos create Qos type=linux-htb other-config:max-rate=1000000000 queues='+q1+' '+q2)
    
    print 'Change S0-eth3 speed'
    q1 = []
    q2 = []
    for i in range(times+right_number):
        q1.append(str(i)+'=@q'+str(i))
        q2.append('-- --id=@q'+str(i)+' create Queue other-config:max-rate='+str(speed_record_left[i]))
    q1 = ','.join(q1)
    q2 = ' '.join(q2)
    CMD = 'ovs-vsctl'
    os.system(CMD+' -- set Port S0-eth3 qos=@newqos -- --id=@newqos create Qos type=linux-htb other-config:max-rate=1000000000 queues='+q1+' '+q2)
    writer.writerow(data)


if __name__ == "__main__":
    HOST, PORT = '192.168.144.134',50000

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    
    left_number = right_number = 32
    left_base = '10.0.0.'
    right_base = '10.0.0.'
    
    times = left_number*right_number+1
    speed_record_left = [500*1000*8]*times + [1000**3]*left_number
    speed_record_right = [500*1000*8]*times + [1000**3]*right_number
    fout = open('class_result.csv','w')
    fieldname = ['timestamp']
    for i in range(left_number):
        fieldname.append(left_base+str(i+1))
        fieldname.append(left_base+str(i+1)+'_speed')
    for i in range(right_number):
        fieldname.append(right_base+str(i+1+100))
        fieldname.append(right_base+str(i+1+100)+'_speed')
    source_provider = '192.168.144.149'
    fieldname = fieldname + [source_provider]
    writer = csv.DictWriter(fout,fieldname)
    writer.writeheader()
    print 'start'
    server.serve_forever()
    '''
    while True:
        s = raw_input('stop?')
        print s
        if s=='stop':
            server.shutdown()
            server.server_close()
            fout.close()
            break
    '''
    server.shutdown()
    server.server_close()
    fout.close()
