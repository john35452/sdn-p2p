from sklearn.ensemble import RandomForestClassifier
#from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
import sys
import time
import os
import numpy as np

path = './new_class/1/'
path2 = './new_class/2/'
path3 = './new_class/3/'
try:
    ftrain = [open(path+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftrain = ftrain + [open(path2+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftrain = ftrain + [open(path3+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftrainy = open(path+'answer.csv','r')
    
except:
    print 'The training data is missing'
    sys.exit()

if len(sys.argv)==3:
    n = int(sys.argv[1])
    depth = int(sys.argv[2])
elif len(sys.argv)==2:
    n = int(sys.argv[1])
    depth = None
else:
    print 'The number of n and d are missing'
    sys.exit()

answer = {}
xtrain = []
ytrain = []
train_seq = []
t1 = time.time()
feature = ftrain[0].readline().split(',')
ftrainy.readline()

for line in ftrain[0]:
    tmp = line[:-1].split(',')
    if tmp[0].startswith('192.168'):
        continue
    train_seq.append(tmp[0])
    xtrain.append([float(tmp[i]) for i in range(1,len(tmp))])
for line in ftrainy:
    tmp = line[:-1].split(',')
    if not tmp[0].startswith('192.168'):
        answer[tmp[0]] = tmp[-1]
for k in train_seq:
    ytrain.append(int(answer[k]))
for k in range(1,len(ftrain)):
    ftrain[k].readline()
    for line in ftrain[k]:
        tmp = line[:-1].split(',')
        if tmp[0].startswith('192.168'):
            continue
        xtrain.append([float(tmp[i]) for i in range(1,len(tmp))])
    for j in train_seq:
        ytrain.append(int(answer[j]))

'''
for line in ftestx:
    tmp = line[:-1].split(',')
    test_seq.append(int(tmp[0]))
    xtest.append([])
    for i in range(1,len(tmp)):
        xtest[-1].append(float(tmp[i]))
'''
print len(xtrain),len(ytrain),len(xtrain[0])
clf = RandomForestClassifier(n_estimators=n,max_depth=depth)
times = 100
accuracy = {}
importance = np.array([0.0]*(len(feature)-1))
for i in range(100):
    clf = clf.fit(xtrain, ytrain)
    scores = clf.score(xtrain, ytrain)
    if scores not in accuracy:
        accuracy[scores] = 1
    else:
        accuracy[scores] += 1 
    importance += clf.feature_importances_

print accuracy
#print clf.feature_importances_

'''
for i in range(len(ytrain)):
    if ytrain[i]!=pytrain[i]:
        print train_seq[i%64],ytrain[i],pytrain[i]
'''
importance = importance/times
print importance
print 'Feature importance'
for i in range(len(importance)):
    if importance[i]==0:
        print feature[i+1]
itemindex = np.where(importance==max(importance))
print itemindex
print feature[itemindex[0][0]+1]
#print feature[importance.index(max(importance))+1]

print 'It takes %lf seconds'%(time.time()-t1)
