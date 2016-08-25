from sklearn.ensemble import RandomForestClassifier
#from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
import sys
import time
import os
import numpy

path_1400 = []
path_1000 = []
path_200 = []
path_400 = []
test = 0
for i in range(5):
    path_1000.append('./new_class/1000s/'+str(i+1)+'/')
for i in range(5):
    #path_200.append('./new_class/200s/'+str(i+1)+'/')
    #path_400.append('./new_class/400s/'+str(i+1)+'/')
    #if i == test:
    #    continue
    #path_400.append('./new_class/400s/'+str(i+1)+'/')
    #path_200.append('./new_class/200s/'+str(i+1)+'/')
    #if i == test:
    #    continue
    path_1400.append('./new_class/1400s/'+str(i+1)+'/')


path = './new_class/200s/'+str(test+1)+'/'
try:
    ftrainx = []
    ftrainy = []
     
    for k in path_1000: 
        ftrainx = ftrainx + [open(k+'train_x_'+str(n+1)+'.csv','r') for n in range(5)]
        ftrainy = ftrainy + [open(k+'train_y_'+str(n+1)+'.csv','r') for n in range(5)]
    ''' 
    for k in path_200:
        ftrainx = ftrainx + [open(k+'train_x_'+str(n+1)+'.csv','r') for n in range(1)]
        ftrainy = ftrainy + [open(k+'train_y_'+str(n+1)+'.csv','r') for n in range(1)]
    for k in path_400:
        ftrainx = ftrainx + [open(k+'train_x_'+str(n+1)+'.csv','r') for n in range(2)]
        ftrainy = ftrainy + [open(k+'train_y_'+str(n+1)+'.csv','r') for n in range(2)]
    '''
    for k in path_1400:
        ftrainx = ftrainx + [open(k+'train_x_'+str(n+1)+'.csv','r') for n in range(7)]
        ftrainy = ftrainy + [open(k+'train_y_'+str(n+1)+'.csv','r') for n in range(7)]
             
   
    ftestx = [open(path+'train_x_'+str(n+1)+'.csv','r') for n in range(1)] 
    ftesty = [open(path+'train_y_'+str(n+1)+'.csv','r') for n in range(1)] 

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

xtrain = []
ytrain = []
xtest = []
ytest = []
t1 = time.time()

for k in range(len(ftrainx)):
    if k==0:
        feature = ftrainx[k].readline().split(',')
    else:
        ftrainx[k].readline()
    seq = []
    answer = {}
    for line in ftrainx[k]:
        tmp = line[:-1].split(',')
        if tmp[0].startswith('192.168'):
            continue
        seq.append(tmp[0])
        xtrain.append([float(tmp[i]) for i in range(1,len(tmp))])
    for line in ftrainy[k]:
        tmp = line[:-1].split(',')
        if not tmp[0].startswith('192.168'):
            answer[tmp[0]] = tmp[-1]
    for j in seq:
        ytrain.append(int(answer[j]))

for k in range(len(ftestx)):
    ftestx[k].readline()
    seq = []
    answer = {}
    for line in ftestx[k]:
        tmp = line[:-1].split(',')
        if tmp[0].startswith('192.168'):
            continue
        seq.append(tmp[0])
        xtest.append([float(tmp[i]) for i in range(1,len(tmp))])
    if k==0:
        test_count = len(xtest)
    for line in ftesty[k]:
        tmp = line[:-1].split(',')
        if not tmp[0].startswith('192.168'):
            answer[tmp[0]] = tmp[-1]
    for j in seq:
        ytest.append(int(answer[j]))

print len(xtrain),len(ytrain),len(xtrain[0]),len(xtest[0]),len(xtest),len(ytest)
#print len(xtrain),len(ytrain)
clf = RandomForestClassifier(n_estimators=n,max_depth=depth)
clf = clf.fit(xtrain, ytrain)
print clf.get_params
joblib.dump(clf,'./model/RF_c.pkl')
scores = clf.score(xtrain, ytrain)
print 'Accuracy:',scores
pytrain =  clf.predict(xtrain)
#print pytrain
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
for i in range(len(ftestx)):
    print 'The result of ',i+1,'part:'
    print clf.score(xtest[i*test_count:(i+1)*test_count],ytest[i*test_count:(i+1)*test_count])
print 'overall:'
print clf.score(xtest,ytest)
pytest = clf.predict(xtest)
value = [[1,0.8,0,0],[0.8,1,0.6,0],[0,0.6,1,0.8],[0,0,0.8,1]]
#print pytest
#print ytest
score_all = 0.0
error_all = 0.0
error_all2 = 0.0
for i in range(len(ftestx)):
    error = 0.0
    error2 = 0.0
    score = 0.0
    for j in range(i*test_count,(i+1)*test_count):
        if abs(pytest[j]-ytest[j])<2:
            error += 1
        if (pytest[j]/2)==(ytest[j]/2):
            error2 += 1
        score += value[ytest[j]][pytest[j]]
    print 'The rough result of ',i+1,'part:'
    print error/test_count
    print error2/test_count
    print score/test_count
    error_all += error
    error_all2 += error2
    score_all += score
print 'The rough result of overall:'
print error_all/len(ytest)
print error_all2/len(ytest)
print score_all/len(ytest)
'''
for i in range(len(ytest)):
    if ytest[i]!=pytest[i]:
        print test_seq[i],ytest[i],pytest[i]
'''
print 'It takes %lf seconds'%(time.time()-t1)
