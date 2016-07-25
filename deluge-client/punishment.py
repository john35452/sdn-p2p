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
        self.data = ''
        while True:
            tmp =  self.request.recv(1024)
            self.data = self.data + tmp
            if tmp[-1]=='\n':
                break
        print "{} wrote:".format(self.client_address[0])
        #print self.data
        # just send back the same data, but upper-cased
        self.request.sendall('Receive '+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        result = json.loads(self.data)
        result[0]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        modify_speed(result)
        
def modify_speed(data):
    global first_time
    average_speed = data[3]
    long_y = data[2]
    y = data[1]
    data = data[0]
    modify_L = False
    modify_R = False
    category = [1,2,5,float('inf')]
    for i in range(left_number):
        name = left_base+'%s'%(i+1)
        if data[name] == 0:
            score[name] += 10
        elif data[name] == 2:
            score[name] -= 5
        elif data[name] == 3:
            score[name] -= 10
        if score[name]>100:
            score[name] = 100
        elif score[name]<0:
            score[name] = 0
        data[name+'_score'] = score[name]
        for j in range(len(category)):
            if category[j]>= y[name]:
                data[name+'_class'] =j
                break
        for j in range(len(category)):
            if category[j]>= long_y[name]:
                data[name+'_class2'] =j
                break
        if first_time:
            score[name] = 50
         
        if score[name] >= 70:
            #speed = speed_record_left[i+1] + 100*1000*8
            speed = speed_record_left[i+1] * 1.1
            if speed>800*1000*8:
                speed = 800*1000*8
            data[name+'_speed'] = speed/8000.0
            for j in range(right_number):
                speed_record_left[i+left_number*j+1] = speed
            speed_record_left[right_number*left_number+i+1] = speed
            if not modify_L:
                modify_L = True
        elif score[name] <=20:
            speed = average_speed[name] * 8 * 0.8
            data[name+'_speed'] = speed/8000.0
            for j in range(right_number):
                speed_record_left[i+left_number*j+1] = speed
            speed_record_left[right_number*left_number+i+1] = speed
            if not modify_L:
                modify_L = True
        elif score[name] <=30:
            #speed = speed_record_left[i+1] - 100*1000*8
            speed = speed_record_left[i+1] * 0.8
            #if speed<100*1000*8:
            #    speed = 100*1000*8
            data[name+'_speed'] = speed/8000.0
            for j in range(right_number):
                speed_record_left[i+left_number*j+1] = speed
            speed_record_left[right_number*left_number+i+1] = speed
            if not modify_L:
                modify_L = True
        else:
            data[name+'_speed'] = speed_record_left[i+1]/8000.0
     
    for i in range(right_number):
        name = right_base+'%s'%(i+1+100)
        if data[name] == 0:
            score[name] += 10
        elif data[name] == 2:
            score[name] -= 5
        elif data[name] == 3:
            score[name] -= 10
        if score[name]>100:
            score[name] = 100
        elif score[name]<0:
            score[name] = 0
        data[name+'_score'] = score[name]
        for j in range(len(category)):
            if category[j]>= y[name]:
                data[name+'_class'] = j
                break
        for j in range(len(category)):
            if category[j]>= long_y[name]:
                data[name+'_class2'] =j
                break
        if first_time:
            score[name] = 50
        #if data[name] == 0:
        if score[name] >=70:
            #speed = speed_record_right[i+1] + 100*1000*8
            speed = speed_record_right[i+1] * 1.1
            if speed >800*1000*8:
                speed = 800*1000*8
            data[right_base+str(i+1+100)+'_speed'] = speed/8000.0
            for j in range(left_number):
                speed_record_right[i+j*right_number+1] = speed
            speed_record_right[right_number*left_number+i+1] = speed
            if not modify_R:
                modify_R = True
        elif score[name] <= 20:
            #speed = speed_record_right[i+1] - 100*1000*8
            #speed = speed_record_right[i+1] * 0.8
            #if speed <100*1000*8:
            #    speed = 100*1000*8
            speed = average_speed[name] * 8 * 0.8
            data[name+'_speed'] = speed/8000.0
            for j in range(left_number):
                speed_record_right[i+j*right_number+1] = speed
            speed_record_right[right_number*left_number+i+1] = speed
            if not modify_R:
                modify_R = True
        #elif data[name] == 3:
        elif score[name] <= 30:
            #speed = speed_record_right[i+1] - 100*1000*8
            speed = speed_record_right[i+1] * 0.8
            #if speed <100*1000*8:
            #    speed = 100*1000*8
            data[name+'_speed'] = speed/8000.0
            for j in range(left_number):
                speed_record_right[i+j*right_number+1] = speed
            speed_record_right[right_number*left_number+i+1] = speed
            if not modify_R:
                modify_R = True
        else:
            data[name+'_speed'] = speed_record_right[i+1]/8000.0
    
    modify_L = modify_R = False
    if modify_L:        
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
    
    if modify_R:    
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
    if first_time:
        first_time = False
    corrent,corrent2 = 0.0,0.0
    number = {0:0,1:0,2:0,3:0}
    number2 = {0:0,1:0,2:0,3:0}
    value = [[1,0.8,0,0],[0.8,1,0.6,0],[0,0.6,1,0.8],[0,0,0.8,1]]
    score1,score2 = 0.0,0.0
    for i in range(right_number):
        name = right_base+'%s'%(i+1)
        if data[name]== data[name+'_class']:
            corrent += 1
        if data[name]== data[name+'_class2']:
            corrent2 += 1
        score1 += value[data[name+'_class']][data[name]]
        score2 += value[data[name+'_class2']][data[name]]
        number[data[name+'_class']] += 1
        number2[data[name+'_class2']] += 1
    for i in range(left_number):
        name = left_base+'%s'%(i+1)
        if data[name]== data[name+'_class']:
            corrent += 1
        if data[name]== data[name+'_class2']:
            corrent2 += 1
        score1 += value[data[name+'_class']][data[name]]
        score2 += value[data[name+'_class2']][data[name]]
        number[data[name+'_class']] += 1
        number2[data[name+'_class2']] += 1
    data['Accuracy'] = corrent/(right_number+left_number)
    data['Accuracy2'] = corrent2/(right_number+left_number)
    data['score'] = score1/(right_number+left_number)
    data['score2'] = score2/(right_number+left_number)
    print 'Accuracy:',data['Accuracy'],data['Accuracy2']
    print 'Score:',data['score'],data['score2']
    print 'Distribution:',number,number2
    for i in range(4):
        data['distribution_'+str(i)] = number[i]
        data['distribution2_'+str(i)] = number2[i]
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
    first_time = True 
    times = left_number*right_number+1
    score = {}
    speed_record_left = [500*1000*8]*times + [1000**3]*left_number
    speed_record_right = [500*1000*8]*times + [1000**3]*right_number
    fout = open('class_result.csv','w')
    fieldname = ['timestamp','Accuracy','score','Accuracy2','score2']
    fieldname = fieldname + ['distribution_'+str(n) for n in range(4)]
    fieldname = fieldname + ['distribution2_'+str(n) for n in range(4)]
    for i in range(left_number):
        fieldname.append(left_base+str(i+1))
        fieldname.append(left_base+str(i+1)+'_score')
        fieldname.append(left_base+str(i+1)+'_class')
        fieldname.append(left_base+str(i+1)+'_class2')
        fieldname.append(left_base+str(i+1)+'_speed')
        score[left_base+str(i+1)] = 50
    for i in range(right_number):
        fieldname.append(right_base+str(i+1+100))
        fieldname.append(right_base+str(i+1+100)+'_score')
        fieldname.append(right_base+str(i+1+100)+'_class')
        fieldname.append(right_base+str(i+1+100)+'_class2')
        fieldname.append(right_base+str(i+1+100)+'_speed')
        score[right_base+str(i+1+100)] = 50
    source_provider = '192.168.144.149'
    fieldname = fieldname + [source_provider]
    writer = csv.DictWriter(fout,fieldname)
    writer.writeheader()
    server.serve_forever()
    server.shutdown()
    server.server_close()
    fout.close()
