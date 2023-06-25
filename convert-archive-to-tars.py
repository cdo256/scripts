import os, sys
import subprocess as sp
dirs = os.listdir('.')
for f in dirs:
    p = sp.Popen(['tar','-cazf','../'+f+'.tar.gz',f])
    print(f+'...')
    p.wait()
