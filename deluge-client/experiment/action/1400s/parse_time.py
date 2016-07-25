import sys
ip = ['user1%s'%(str(n+1).zfill(2)) for n in range(32)]
ip = ip + ['user2%s'%(str(n+1).zfill(2)) for n in range(32)]
f = {}
try:
    for k in ip:
        f[k] = open(sys.argv[1]+k,'r')
    fout = open('starttime.csv','w')
except:
    print 'Error with files'
    sys.exit()

seq = {}
start = {}
data = {}
for k in ip:
    seq[k] = []
    start[k] = []
    for line in f[k]:
        if len(start[k])>2:
            break
        if not (line[0]=='3' or line[0]=='s'):
            continue
        line = line[:-1].split()
        if line[0][0]=='3':
            seq[k].append(line[1][3])
        elif line[0][0]=='s':
            start[k].append(int(line[1]))
    #print seq,start
    data[k] = {seq[k][0]:0}
    total = 0
    for i in range(1,len(seq[k])):
        total += start[k][i-1]
        data[k][seq[k][i]] = total
    fout.write(k+','+str(data[k]['a'])+','+str(data[k]['b'])+','+str(data[k]['c'])+'\n')

fout.close()
        
    
