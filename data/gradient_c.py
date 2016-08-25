#from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
import sys
import time
import os
import numpy

path = './new_class/1/'
path2 = './new_class/2/'
path3 = './new_class/3/'
path4 = './new_class/4/'
path5 = './new_class/5/'

path6 = './new_class/200s/'
try:
    ftrain = [open(path+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftrain = ftrain + [open(path2+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftrain = ftrain + [open(path3+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftrain = ftrain + [open(path4+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    #ftrain = ftrain + [open(path5+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftrainy = open(path+'answer.csv','r')
    

    ftest = [open(path5+'train_x_'+str(n+1)+'.csv','r') for n in range(5)] 
    ftesty = open(path5+'answer.csv','r')

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
answer2 = {}
xtrain = []
ytrain = []
xtest = []
ytest = []
train_seq = []
test_seq = []
t1 = time.time()
feature = ftrain[0].readline().split(',')
ftrainy.readline()
ftest[0].readline()
ftesty.readline()

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

for line in ftest[0]:
    tmp = line[:-1].split(',')
    if tmp[0].startswith('192.168'):
        continue
    test_seq.append(tmp[0])
    xtest.append([float(tmp[i]) for i in range(1,len(tmp))])
test_count = len(xtest)
for line in ftesty:
    tmp = line[:-1].split(',')
    if not tmp[0].startswith('192.168'):
        answer2[tmp[0]] = tmp[-1]
for k in test_seq:
    ytest.append(int(answer2[k]))
for k in range(1,len(ftest)):
    ftest[k].readline()
    for line in ftest[k]:
        tmp = line[:-1].split(',')
        if tmp[0].startswith('192.168'):
            continue
        xtest.append([float(tmp[i]) for i in range(1,len(tmp))])
    for j in train_seq:
        ytest.append(int(answer[j]))
'''
for line in ftestx:
    tmp = line[:-1].split(',')
    test_seq.append(int(tmp[0]))
    xtest.append([])
    for i in range(1,len(tmp)):
        xtest[-1].append(float(tmp[i]))
'''
#print len(xtrain),len(ytrain),len(xtrain[0]),len(xtest[0]),len(xtest),len(ytest)
print len(xtrain),len(ytrain)
clf = GradientBoostingClassifier(n_estimators=n,max_depth=depth)
clf = clf.fit(xtrain, ytrain)
print clf.get_params
joblib.dump(clf,'./model/RF_c.pkl')
scores = clf.score(xtrain, ytrain)
print 'Accuracy:',scores
pytrain =  clf.predict(xtrain)
print pytrain.shape
'''
for i in range(len(ytrain)):
    if ytrain[i]!=pytrain[i]:
        print train_seq[i%64],ytrain[i],pytrain[i]
'''
print 'Feature importance'
print clf.feature_importances_
importance = clf.feature_importances_
for i in range(len(importance)):
    if importance[i]==0:
        print feature[i+1]
itemindex = numpy.where(importance==max(importance))
print itemindex
print 'biggest:',feature[itemindex[0][0]+1],importance[itemindex]
#print feature[importance.index(max(importance))+1]
#fstat.write(str(n)+','+str(depth)+'\n')
#fstat.write('Ein,'+str(scores)+'\n')
for i in range(len(ftest)):
    print 'The result of ',i,'part:'
    print clf.score(xtest[i*test_count:(i+1)*test_count],ytest[i*test_count:(i+1)*test_count])
print 'overall:'
print clf.score(xtest,ytest)
pytest = clf.predict(xtest)
print pytest
print ytest
'''
for i in range(len(ytest)):
    if ytest[i]!=pytest[i]:
        print test_seq[i],ytest[i],pytest[i]
'''
print 'It takes %lf seconds'%(time.time()-t1)
