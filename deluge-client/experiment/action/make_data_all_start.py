import sys
import random
if len(sys.argv)<3:
    print 'Usage:python make_data.py [filename] [rate]'
    sys.exit()

speed = [100,500,1000]
speed = [500]
file_list = ['1GBa.txt.torrent','1GBb.txt.torrent','1GBc.txt.torrent']
files = list(file_list)
time_range = 1000
time_start = [0]
download = speed[random.randint(0,len(speed)-1)]
upload = download + random.randint(0,download/2)-download/4
download = upload = speed[0]
print 'start:',time_start
print 'files:',files
print 'download:',download
print 'upload:',upload
print 'rate:',sys.argv[2]
with open(sys.argv[1],'w') as f:
    f.write('2\nrate '+sys.argv[2]+'\n')
    for k in range(len(files)):
        f.write('3 '+files[k]+'\n')
        f.write('ds '+files[k]+' '+str(download)+'\n')
        f.write('us '+files[k]+' '+str(upload)+'\n')
        f.write('1\n')
    for k in range(len(files)):
        f.write('7 '+files[k]+'\n')
    f.write('s '+str(time_range)+'\n')
    for k in file_list:
        f.write('f '+k+'\n')
    f.write('sf\n10\n')
