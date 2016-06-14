import os
import sys
if len(sys.argv)<2:
    print 'Usage:python send_data [directory_name+"/"]'
    sys.exit()
files = ['data_client.csv','data_switch.csv','data_tracker_peer.csv','data_tracker_request.csv']
os.system('scp data_* john@192.168.144.134:~/sdn-p2p/data/'+sys.argv[1])
