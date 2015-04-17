import numpy as np
from collections import Counter
from numpy import array, zeros, argmin, inf
from numpy.linalg import norm
import sys,argparse


DATA_PATH='/others/abilng/Database/MSR2-abil/test/data_out/'
GroundTruthFile="/others/abilng/Database/MSR2-abil/Videos/groundtruth.txt";
PrintProgress=True

def dtw(x, y, dist=lambda x, y: norm(x - y, ord=1)):
    """ Computes the DTW of two sequences.

    :param array x: N1*M array
    :param array y: N2*M array
    :param func dist: distance used as cost measure (default L1 norm)

    Returns the minimum distance, the accumulated cost matrix and the wrap path.

    """
    x = array(x)
    if len(x.shape) == 1:
        x = x.reshape(-1, 1)
    y = array(y)
    if len(y.shape) == 1:
        y = y.reshape(-1, 1)

    r, c = len(x), len(y)

    D = zeros((r + 1, c + 1))
    D[0, 1:] = inf
    D[1:, 0] = inf

    for i in range(r):
        for j in range(c):
            D[i+1, j+1] = dist(x[i], y[j])

    for i in range(r):
        for j in range(c):
            D[i+1, j+1] += min(D[i, j], D[i, j+1], D[i+1, j])

    D = D[1:, 1:]

    dist = D[-1, -1] / sum(D.shape)

    return dist, D



def getMSR2GroundTruth(GroundTruthFile):
	labels = {}
	with open(GroundTruthFile) as f:
		data = f.read();
		for line in data.splitlines():
			if line[0]=='#':
				#comment
				continue;
			seg={};
			words=line.split()
			#video_name, left, width, top, height, start, time duration, action(1-clapping-2-waving-3-boxing)
			seg['action']=int(words[7])
			seg['start']=int(words[5])
			seg['length']=int(words[6])
			video=(words[0].strip('".avi'));
			try:
				labels[video]
			except KeyError:
				labels[video]=list();
			finally:
				labels[video].append(seg);
	return labels;

def getRes(groundTruth, qFile, classes=[], nFiles=54):

	targetScore={}
	nonTargetScore={}
	Tp={}
	Fp={}
	q={}

	for cls in classes:
		targetScore[cls]=list()
		nonTargetScore[cls]=list()
		Tp[cls]=Fp[cls]=0
		q[cls]=None

	##############################
	#READ Q File

	f = open(DATA_PATH+'/'+str(qFile)+'.avi.txt','r');
	f.readline();
	dat=np.loadtxt(f);
	f.close()

	for label in groundTruth[str(qFile)]:
		if label['action']  not in classes:
			continue
		start=label['start']
		end=label['start']+label['length']
		q[label['action']]=dat[start:end]

	############

	##For each File
	for name in xrange(1,nFiles+1):
		filename=str(name)
		#if filename==str(qFile):
		#	continue

		#init var		

		#read data
		f = open(DATA_PATH+'/'+filename+'.avi.txt','r');
		f.readline();
		dat=np.loadtxt(f);
		f.close()

		#print filename,Query
		if PrintProgress:
			sys.stderr.write('[Query '+str(qFile)+' ]Testing on File:'+filename+'\r')


		#for each label
		for label in groundTruth[filename]:
			
			orgLabel=label['action']
			if orgLabel not in classes:
				continue

			start=label['start']
			end=label['start']+label['length']

			distance ={}
			for cls in classes:
				#dtw scores
				if q[cls] is None:
					continue
				distance[cls], _ =  dtw(dat[start:end], q[cls]) 

				if cls==orgLabel:
					targetScore[orgLabel].append(distance[cls])
				else:
					nonTargetScore[orgLabel].append(distance[cls])
			preLabel=min(distance, key=distance.get);


			if preLabel==orgLabel:
				Tp[preLabel]+=1
			else:
				Fp[preLabel]+=1

	if PrintProgress:
		sys.stderr.write('[Query '+str(qFile)+' ]Testing on File: [DONE]\n')
	return targetScore,nonTargetScore,Tp,Fp


def precision(Tp,Fp,Total):
	retrieved =Counter(Tp)+Counter(Fp)
	prec=dict()
	for (key,val) in retrieved.iteritems():
		prec[key]=float(Tp[key])/retrieved[key]
	
	prec['Avg'] = sum(i for i in Tp.itervalues())/sum(i for i in retrieved.itervalues())
	return prec

def recall(Tp,Fp,Total):
	rec=dict()
	for (key,val) in Total.iteritems():
		rec[key]=float(Tp[key])/Total[key]
	rec['Avg'] = sum(i for i in Tp.itervalues())/sum(i for i in Total.itervalues())
	return rec

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='GMM Testing')
	parser.add_argument('-v','--verbose', action='store_true')
	parser.add_argument('targetFile')
	parser.add_argument('nonTargetFile')

	args = parser.parse_args()
	PrintProgress = args.verbose

	targetFile = args.targetFile
	nonTargetFile = args.nonTargetFile
	groundTruth = getMSR2GroundTruth(GroundTruthFile);
	
	q=[2,11,44,50,32,8,45,33,20,25]

	frameLen=15
	nClass =3
	nFiles=54
	
	classes = range(1,nClass+1)

	AvgTp = Counter({1:0,2:0,3:0})
	AvgFp = Counter({1:0,2:0,3:0})

	targetFptr=file(targetFile,'w');
	nonTargetFptr=file(nonTargetFile,'w');

	print "|| Query |",
	for cls in classes:
		print "Tp(%02d) | Fp(%02d) |"%(cls,cls),
	print "Tp(Avg) | Fp(Avg) ||"

	print "||=======",
	for cls in classes:
		print "======== ========",
	print "===================||" 

	for qFile in q:
		(targetScore,nonTargetScore,Tp,Fp)=getRes(groundTruth,qFile,classes,nFiles)
		
		AvgTp +=Counter(Tp)
		AvgFp +=Counter(Fp)

		print "||  %2d   |"%(qFile),
		for cls in classes:
			print "  %02d   |   %02d   |"%(Tp[cls],Fp[cls]),
		print "%.04f | %.04f ||"%(
			sum(i for i in Tp.itervalues())/float(len(classes)),
			sum(i for i in Fp.itervalues())/float(len(classes)))

		for scores in targetScore.itervalues():
			for score in scores:
				targetFptr.write("%.5f"%score+"\n")

		for scores in nonTargetScore.itervalues():
			for score in scores:
				nonTargetFptr.write("%.5f"%score+"\n")


	targetFptr.close()
	nonTargetFptr.close()

	n=float(len(q))
	for (key,val) in AvgTp.iteritems():
		AvgTp[key] = AvgTp[key]/n
	for (key,val) in AvgFp.iteritems():
		AvgFp[key] = AvgFp[key]/n

	print "||  Avg  |",
	for cls in classes:
		print "  %02d   |   %02d   |"%(AvgTp[cls],AvgFp[cls]),
	print "%.04f | %.04f ||"%(
		sum(i for i in AvgTp.itervalues())/float(nClass),
		sum(i for i in AvgFp.itervalues())/float(nClass))	

