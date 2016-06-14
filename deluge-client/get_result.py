import os
import sys

files = filter(lambda x:x.endswith('answer.txt'),os.listdir('.'))
print files
with open('answer.txt','w') as fout:
    for k in files:
        with open(k,'r') as f:
            fout.write(k[:-11]+' '+f.read()+'\n')
