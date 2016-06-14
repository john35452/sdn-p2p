import sys
import os
import random
left = 32
right = 32
rate = [0,0.5,1,2,1000]
for i in range(4):
    print 'group:',(i+1)
    for j in range(left/4):
        new_rate = random.uniform(rate[i],rate[i+1])
        os.system('python make_data.py '+sys.argv[1]+'/user1'+str(i*(left/4)+j+1).zfill(2)+' '+str(new_rate))
    for j in range(right/4):
        new_rate = random.uniform(rate[i],rate[i+1])
        os.system('python make_data.py '+sys.argv[1]+'/user2'+str(i*(right/4)+j+1).zfill(2)+' '+str(new_rate))
 
