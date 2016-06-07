import os
import sys
import time
import base64
from deluge_client import DelugeRPCClient
class p2p_client():
    def __init__(self,com_id,host_id):
        self.com_id = int(com_id)
        self.host_id = int(host_id)
        self.port = 62000 + (self.com_id-1)*100 + (self.host_id-1)
        self.home_dir = './experiment/'
        self.account = ''
        self.password = ''
        
    def config(self):
        dir_type = ['Config','Log','PID','Host_Local_Storage','NewTorrent']
        ids = 'Com' + str(self.com_id) + '_Host' + str(self.host_id)
        for k in dir_type:
            path = self.home_dir + k + '/' + ids
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except:
                    print 'Error: error when making directories!! dir:',path
                    sys.exit()
 
        log_file = self.home_dir + 'Log/'+ ids + '/'+ ids + '.txt'
        pid_file = self.home_dir + 'PID/'+ ids + '/'+ ids + '.txt'
        if not os.path.isfile(log_file):
            try:
                open(log_file,'w').close()
            except:
                print 'Error when writing log file'
                sys.exit()
        if not os.path.isfile(pid_file):
            try:
                open(pid_file,'w').close()
            except:
                print 'Error when writing pid file'
                sys.exit()
    
    def get_user_info(self):
        config = self.home_dir + 'Config/Com' + str(self.com_id)+'_Host' + str(self.host_id) + '/auth'
        try:
            f = open(config,'r')
            data = f.read().split(':')
            self.account = data[0]
            self.password = data[1]
            f.close()
        except:
            print 'Error: error when getting Accoung/Password'
            sys.exit()

    def start_daemon(self):
        ids = 'Com' + str(self.com_id) + '_Host' + str(self.host_id)
        config_path = self.home_dir + 'Config/' + ids
        log_file = self.home_dir + 'Log/'+ ids + '/'+ ids + '.txt'
        pid_file = self.home_dir + 'PID/'+ ids + '/'+ ids + '.txt'
        command = 'deluged -c %s -l %s -P %s -p %s' % (config_path, log_file, pid_file, str(self.port))
        os.system(command)
        time.sleep(5)

    def shutdown(self):
        self.client.call('daemon.shutdown')

    def login(self):
        self.client =  DelugeRPCClient('127.0.0.1', self.port, self.account, self.password)
        self.client.connect()
   
    def get_session_state(self):
        return self.client.call('core.get_session_state')

    def clean_session(self):
        item = self.get_session_state()
        for k in item:
            self.remove_torrent(k)

    def get_method_list(self):
        method = sorted(list(self.client.call('daemon.get_method_list')))
        for k in method:
            print k

    def get_torrent_status(self,hashid):
        return self.client.call('core.get_torrent_status',hashid,'')

    def get_torrents_status(self):
        return self.client.call('core.get_torrents_status',{},[])
   
    def add_torrent(self,file_name):
        torrent_file = self.home_dir + 'torrent/' + file_name
        download_path = self.home_dir + 'Host_Local_Storage/' + 'Com' + str(self.com_id)+'_Host' + str(self.host_id)
        if not os.path.isdir(download_path):
            try:
                os.makedirs(download_path)
            except:
                print 'Error: error when making download directories'
                sys.exit()
        self.client.call('core.add_torrent_file',torrent_file,base64.encodestring(open(torrent_file,'rb').read()),{'add_paused':True, 'download_location':download_path})
 
    def remove_torrent(self,hashid,remove_data=True):
        self.client.call('core.remove_torrent',hashid,remove_data)

    def create_torrent(self,file_dst,comment='',create_by=''):
        source = '/home/john/p2p/file/'+file_dst
        torrent_location = self.home_dir + 'NewTorrent/' + 'Com' + str(self.com_id)+'_Host' + str(self.host_id)+'/'+file_dst+'.torrent'
        tracker = 'http://192.168.144.126:9010/'
        piece_length = 30768
        webseeds = ''
        add_to_session = True
        private = False
        trackers = ''
        self.client.call('core.create_torrent',source,tracker,piece_length,comment,torrent_location,webseeds,private,create_by,trackers,add_to_session)
  
    def resume_torrent(self,torrents):
        self.client.call('core.resume_torrent',torrents)

    def pause_torrent(self,torrents):
        self.client.call('core.pause_torrent',torrents)

    def set_torrent_max_download_speed(self,torrent,value):
        self.client.call('core.set_torrent_max_download_speed',torrent,value)
 
    def set_torrent_max_upload_speed(self,torrent,value):
        self.client.call('core.set_torrent_max_upload_speed',torrent,value) 
    
    def get_session_status(self,key=''):
        return self.client.call('core.get_session_status',key)
