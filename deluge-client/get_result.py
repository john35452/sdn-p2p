import os
import sys

files = filter(lambda x:x.endswith('answer.txt'),os.listdir('.'))
print files
with open('answer.csv','w') as fout:
    fout.write('ip,predict_ratio,real_ratio,predict_class,real_class\n')
    for k in files:
        with open(k,'r') as f:
            fout.write(k[:-11]+','+f.read()+'\n')
