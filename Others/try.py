import numpy as np
from sklearn.mixture import GMM
from sklearn.externals import joblib
import os


def loadAllData(filenames):
	data = None
	print 'Loading Data .....................',
	i = 0;
	for filename in filenames:
		i+=1;
		print '\rLoading Data .......................[{0}/{1}]'.format(i,len(filenames)),
		f = open(filename,'r')
		f.readline();
		tmpdata=np.loadtxt(f);
		if data is None: 
			data = tmpdata;
		else :
			data = np.vstack([data,tmpdata])

	print '\rLoading Data ....................... [DONE]'
	return data

def trainGMM(filenames,n_components=10):
	outdir = "GMMs/GMM_"+str(n_components)
	outModelfile = outdir+"/gmm"


	data = loadAllData(filenames)
	g = GMM(n_components=n_components)
	print 'Training GMM .......................',
	g.fit(data)
	print '\rTraining GMM ....................... [DONE]'
	
	print 'Saving GMM ...............to {0}'.format(outModelfile),
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	joblib.dump(g,outModelfile)
	print '\rSaving GMM ....................... [DONE]'

def projectData(filenames,n_components):
	
	outdir="data/GMM_"+str(n_components);
	inModelfile = "GMMs/GMM_"+str(n_components)+"/gmm"

	print 'Loading GMM.............from {0}'.format(inModelfile),
	g=joblib.load(inModelfile)
	print '\rLoading GMM....................... [DONE]'

	i = 0;
	if not os.path.exists(outdir):
		os.makedirs(outdir)

	print 'Projecting on GMMs................',
	for filename in filenames:
		i+=1;
		print '\rProjecting on GMMs..................[{0}/{1}]'.format(i,len(filenames)),
		f = open(filename,'r')
		f.readline();
		tmpdata=np.loadtxt(f);
		x=g.score_samples(tmpdata);
		x1=x[1]
		outfile=outdir+"/"+ os.path.basename(filename)
		np.savetxt(outfile,x1,fmt='%f')
	print '\rProjecting on GMMs.................. [DONE]'

def main(n_components):	
	trainfilenames = [
	#"/others/abilng/data_in/1.avi.txt",
	#"/others/abilng/data_in/2.avi.txt", 
	#"/others/abilng/data_in/3.avi.txt",
	"/others/abilng/data_in/4.avi.txt",
	"/others/abilng/data_in/5.avi.txt",
	"/others/abilng/data_in/6.avi.txt",
	#"/others/abilng/data_in/7.avi.txt",
	#"/others/abilng/data_in/8.avi.txt",
	#"/others/abilng/data_in/9.avi.txt",
	"/others/abilng/data_in/10.avi.txt",
	"/others/abilng/data_in/11.avi.txt",
	"/others/abilng/data_in/12.avi.txt",
	#"/others/abilng/data_in/13.avi.txt",
	#"/others/abilng/data_in/14.avi.txt",
	#"/others/abilng/data_in/15.avi.txt",
	#"/others/abilng/data_in/16.avi.txt"
	]

	AllFiles = [
	"/others/abilng/data_in/1.avi.txt",
	"/others/abilng/data_in/2.avi.txt", 
	"/others/abilng/data_in/3.avi.txt",
	"/others/abilng/data_in/4.avi.txt",
	"/others/abilng/data_in/5.avi.txt",
	"/others/abilng/data_in/6.avi.txt",
	"/others/abilng/data_in/7.avi.txt",
	"/others/abilng/data_in/8.avi.txt",
	"/others/abilng/data_in/9.avi.txt",
	"/others/abilng/data_in/10.avi.txt",
	"/others/abilng/data_in/11.avi.txt",
	"/others/abilng/data_in/12.avi.txt",
	"/others/abilng/data_in/13.avi.txt",
	"/others/abilng/data_in/14.avi.txt",
	"/others/abilng/data_in/15.avi.txt",
	"/others/abilng/data_in/16.avi.txt"
	]
	trainGMM(trainfilenames,n_components=n_components) 
	projectData(AllFiles, n_components=n_components)

if __name__ == '__main__':
	#import sys
	#main(int(sys.argv[1]))
	for x in xrange(2,12):
		main(x)