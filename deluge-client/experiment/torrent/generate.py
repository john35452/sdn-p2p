import time
file_list = ['a','b','c']
times = 1<<30
t1 = time.time()
for k in file_list:
    i = 0
    with open('1GB'+k+'.txt','w') as f:
        while i<times:
            f.write(k)
            i += 1
print 'It takes %lf seconds'%(time.time()-t1)
