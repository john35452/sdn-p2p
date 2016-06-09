import sys
import random
if len(sys.argv)<3:
    print 'Usage:python make_data.py [filename] [rate]'
    sys.exit()

speed = [100,500,1000]
file_list = ['100MBa.txt.torrent','100MBb.txt.torrent','100MBc.txt.torrent']
files = list(file_list)
time_range = 500
time_start = [0]
cut = time_range/len(file_list)
for k in range(len(file_list)-1):
    time_start.append(random.randint(k*cut,(k+1)*cut))
random.shuffle(files)
download = speed[random.randint(0,2)]
upload = speed[random.randint(0,2)]
print 'start:',time_start
print 'files:',files
print 'download:',download
print 'upload:',upload
with open(sys.argv[1],'w') as f:
    f.write('2\nrate '+sys.argv[2]+'\n')
    for k in range(len(files)):
        f.write('3 '+files[k]+'\n')
        f.write('ds '+files[k]+' '+str(download)+'\n')
        f.write('us '+files[k]+' '+str(upload)+'\n')
        f.write('7 '+files[k]+'\n')
        f.write('s '+str(time_start[k])+'\n')
        f.write('1\n')
    f.write('s 30')
    for k in file_list:
        f.write('f '+k+'\n')
    f.write('sf\n10\n')

