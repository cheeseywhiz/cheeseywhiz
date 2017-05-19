import sys
import os
import time
t0=time.clock()
def filename():
	if not 'C:\\' in sys.argv[1]: return ("'"+os.getcwd()+"/"+str(sys.argv[1])+"'").replace('\\','/')
	else: return ("'"+str(sys.argv[1])+"'").replace('\\','/')

if sys.argv[1] in ['-h']: print('\nTHIS_FILEPATH (type=str) in source file will be replaced as expected\n\n-h -help /?: This helpscreen\n<filename>: File to be executed')
else:
	with open(sys.argv[1],'r') as file: exec((file.read()).replace('THIS_FILEPATH',filename()))
print(time.clock()-t0)