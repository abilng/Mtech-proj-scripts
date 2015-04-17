import numpy as np
from collections import Counter
import sys

GMM_PATH='/others/abilng/Database/MSR2-abil/test/data_out/data/GMM_'
GroundTruthFile="/others/abilng/Database/MSR2-abil/Videos/groundtruth.txt";

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

def getRes(groundTruth,qFile,cluster,threshold=0.5,frameLen=15,nClass =3,nFiles=54):

	Tp={}
	Fp={}
	Total={}
	q={}

	for cls in xrange(1,nClass+1):
		Tp[cls]=Fp[cls]=Total[cls]=0
		q[cls]=None		

	##############################
	#READ Q File

	f = open(GMM_PATH+str(cluster)+'/'+str(qFile)+'.avi.txt','r');
	f.readline();
	dat=np.loadtxt(f);
	f.close()

	for label in groundTruth[qFile]:
		start=label['start']+5
		end=label['start']+label['length']-5
		q[label['action']]=np.mean(dat[start:end],0)

	############


	##For each File
	for name in xrange(1,nFiles+1):
		filename=str(name)
		if filename==qFile:
			continue

		sys.stderr.write('[Query '+str(qFile)+' ]Testing on File:'+filename+'\r')

		#init var		
		preLabel={}
		orgLabel={}

		for cls in xrange(1,nClass+1):
			preLabel[cls]=list()
			orgLabel[cls]=list()

		#read data
		f = open(GMM_PATH+str(cluster)+'/'+filename+'.avi.txt','r');
		f.readline();
		dat=np.loadtxt(f);
		f.close()


		for cls in xrange(1,nClass+1):
			#dot product and thresholding
			if q[cls] is None:
				continue

			v=np.asarray([False]+[(np.dot(x,q[cls])>threshold) for x in dat]+[False])
			ind=np.where(v[:-1] != v[1:])[0]
			indD = np.diff(ind);

			#find ranges
			prevend=0;
			for i in xrange(1,len(indD),2):
				if indD[i] < frameLen*2:
					continue;
				start=ind[i]+1;
				end=ind[i+1]-1;
				if(prevend!=0 and (start-prevend)<(frameLen)):
					(start_old,end_old)=preLabel[cls][-1];
					preLabel[cls][-1]=(start_old,end);
				else:
					preLabel[cls].append((start,end))
				prevend=end;

		#find orginal ranges

		for label in groundTruth[filename]:
			start=label['start']
			end=label['start']+label['length']
			orgLabel[label['action']].append((start,end))

		#compare orginal and predicted ranges

		for cls in xrange(1,nClass+1):
			for x in preLabel[cls]:
				inside = any(( ((x[0]>=y[0] and x[1]<=y[1]) or (x[1]>=y[0] and x[1]<=y[1]) or
					((x[0]>=y[0] and x[0]<=y[1]))) for y in orgLabel[cls]))
				if inside:
					Tp[cls]+=1
				else:
					Fp[cls]+=1
					#print cls,x,orgLabel[cls]
			Total[cls]+=len(orgLabel[cls])
	sys.stderr.write('[Query '+str(qFile)+' ]Testing on File: [DONE]\n')
	return Tp,Fp,Total


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
	groundTruth = getMSR2GroundTruth(GroundTruthFile);
	
	q=[2,11,44,50,32,8,45,33,20,25]

	frameLen=15
	nClass =3
	nFiles=54
	

	print "|| GMM | Thresh |",
	for x in xrange(0,nClass):
		print "Prec(%02d) | Recal(%02d) |"%(x+1,x+1),
	print "Prec(Avg) | Recal(Avg) | F-score  ||"

	print "||===== ========",
	for x in xrange(0,nClass):
		print "========== ===========",
	print "=========== ============ ==========||"


	for cluster in xrange(3,15):
		for threshold in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]:
			pass

			AvgTp = Counter({1:0,2:0,3:0})
			AvgFp = Counter({1:0,2:0,3:0})
			AvgTo = Counter({1:0,2:0,3:0})		

			for qFile in q:
				(Tp,Fp,Total)=getRes(groundTruth,str(qFile),cluster,threshold,frameLen,nClass,nFiles)
				AvgTp +=Counter(Tp)
				AvgFp +=Counter(Fp)
				AvgTo +=Counter(Total)
				#print "%d\t:%02d/%02d/%02d\t%02d/%02d/%02d\t%02d/%02d/%02d\t" %(
				#	qFile,Tp[1],Fp[1],Total[1],Tp[2],Fp[2],Total[2],Tp[3],Fp[3],Total[3])
		
			n=float(len(q))
			for (key,val) in AvgTp.iteritems():
				AvgTp[key] = AvgTp[key]/n
			for (key,val) in AvgFp.iteritems():
				AvgFp[key] = AvgFp[key]/n
			for (key,val) in AvgTo.iteritems():
				AvgTo[key] = AvgTo[key]/n
		
			#print "%d %.2f\t:%.02f/%.02f/%.02f\t%.02f/%.02f/%.02f\t%.02f/%.02f/%.02f\t" %(
			#	AvgTp[1],AvgFp[1],AvgTo[1],
			#	AvgTp[2],AvgFp[2],AvgTo[2],
			#	AvgTp[3],AvgFp[3],AvgTo[3])
		
			prec = precision(AvgTp, AvgFp, AvgTo);
			rec = recall(AvgTp, AvgFp, AvgTo);

			fscore=2*(prec['Avg']*rec['Avg'])/(prec['Avg']+rec['Avg'])

			print "||  %2d |    %2.1f |"%(cluster,threshold),
			for cls in xrange(1,nClass+1):
				print "  %.04f |    %.04f |"%(prec[cls],rec[cls]),
			print "   %.04f |     %.04f |   %.04f ||"%(prec['Avg'],rec['Avg'],fscore)