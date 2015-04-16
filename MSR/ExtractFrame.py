#! /usr/bin/env python2.7
import numpy as np
import cv2
import os
import random
from numpy import cumsum
from multiprocessing.pool import ThreadPool
from collections import deque


#threadn = int(cv2.getNumberOfCPUs()*0.6)
#pool = ThreadPool(processes = threadn)
#pending = deque()

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


def getMSRGroundTruth(GroundTruthFile):
	labels = {}
	with open(GroundTruthFile) as f:
		data = f.read();
		for line in data.splitlines():
			if line[0]=='#':
				#comment
				continue;
			seg={};
			words=line.split()
			#left-width-top-height-start-length-video-action(1-clapping-2-waving-3-boxing)
			seg['action']=int(words[7])
			seg['start']=int(words[4])
			seg['length']=int(words[5])
			video=(words[6]);
			try:
				labels[video]
			except KeyError:
				labels[video]=list();
			finally:
				labels[video].append(seg);
	return labels;


def process_frame(frame,count,scale,prevframe=None):
	# some intensive computation...
	frame = cv2.resize(frame,None, fx=scale, fy=scale, interpolation = cv2.INTER_LINEAR)
	gray = cv2.cvtColor( frame, cv2.COLOR_RGB2GRAY )
	edges = cv2.Canny(gray,100,300)
	if prevframe is None:
		difframe=edges
	else:
		prevframe = cv2.resize(prevframe,None, fx=scale, fy=scale, interpolation = cv2.INTER_LINEAR)
		prevframe = cv2.cvtColor( prevframe, cv2.COLOR_RGB2GRAY )
		difframe = cv2.absdiff(gray,prevframe)
	outframe=np.dstack((gray,edges,difframe))
	return (outframe/float(255)),count

def getFrames(File,scale,parallel=False):
	
	cap = cv2.VideoCapture(File)
	cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,0)

	framecount = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)*scale)
	height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)*scale)

	frames = np.zeros((framecount,height,width,3));
	prevframe=None
	frame=None

	count = 0
	if parallel:
	
		while True:
			if len(pending) < threadn:
				prevframe=frame
				ret, frame = cap.read()
				if ret:
					if not prevframe is None:	
						task = pool.apply_async(process_frame, (frame.copy(), count,scale,prevframe.copy()))
					else:
						task = pool.apply_async(process_frame, (frame.copy(), count,scale,None))
					pending.append(task)
					count+=1
				else:
					if(len(pending)==0): break;
	
			while len(pending) > 0 and pending[0].ready():
				(res,t0) = pending.popleft().get()
				try:
					frames[t0] = res;
				except IndexError:
					print("Error: In CV_CAP_PROP_FRAME_COUNT, resizing frames");
					newframes = np.zeros((t0+1,height,width,3));
					newframes[0:-1] = frames
					newframes[-1] = res
					frames = newframes; 

	else:
	
		while True:
			prevframe=frame
			ret, frame = cap.read()
			if ret:
				(res,t0) = process_frame(frame,count,scale,prevframe)
				try:
					frames[t0] = res;
				except IndexError:
					print("Error: In CV_CAP_PROP_FRAME_COUNT, resizing frames");
					newframes = np.zeros((t0+1,height,width,3));
					newframes[0:-1] = frames
					newframes[-1] = res
					frames = newframes; 
				count+=1
			else:
				break
		cap.release()
	
	print frames.shape
	return frames




def saveLabeledParts(scale,groundTruth,directory,skipList=[],testPer=0.1,valPer=0.1):
	labelNames=["clapping","waving","boxing"]
	trainPer = 1-(testPer+valPer);
		
	if not os.path.exists(directory): os.mkdir(directory)
	print "Created Out Directory:"+directory
	

	trainFiles= [ open(directory+os.sep+name+"_train.txt",'w') for name in labelNames]
	testFiles= [ open(directory+os.sep+name+"_test.txt",'w') for name in labelNames]
	valFiles= [ open(directory+os.sep+name+"_val.txt",'w') for name in labelNames]
	
	width = int(320*scale)
	height = int(240*scale)
	cmaps=3
	
	for f in trainFiles: f.write(str(height*width*cmaps)+'\n')
	for f in testFiles: f.write(str(height*width*cmaps)+'\n')
	for f in valFiles: f.write(str(height*width*cmaps)+'\n')
	


	for (fileName,labels) in groundTruth.items():
		#restit
		print 'loading...',fileName,'.avi '
		if fileName in skipList:
			print "skiping {0}.avi ... ".format(fileName)
			continue;
		frames=getFrames(fileName+".avi",scale);
		
		for label in labels:
			#print label,label['length']+label['start']
			ind = [i for i in xrange(label['start'],(label['length']+label['start'])) ]
			random.shuffle(ind)
			stops=map(int, cumsum([trainPer,testPer,valPer])*len(ind));
			trainInd,testInd,valInd = [ind[a:b] for a, b in zip([0]+stops, stops)];
	
			filehandle = trainFiles[label['action']-1]
			out = [ (frames[i]).flatten() for i in trainInd]
			np.savetxt(filehandle,out, fmt='%f', delimiter=' ');
			filehandle.flush();
	
			filehandle = testFiles[label['action']-1]
			out = [ (frames[i]).flatten() for i in testInd]
			np.savetxt(filehandle,out, fmt='%f', delimiter=' ');
			filehandle.flush();
	
			filehandle = valFiles[label['action']-1]
			out = [ (frames[i]).flatten() for i in valInd]
			np.savetxt(filehandle,out, fmt='%f', delimiter=' ');
			filehandle.flush();
		#for labels
	print frames[-1:].shape

def saveVideoFile(fileName,scale,directory):
	if not os.path.exists(directory): os.mkdir(directory)
	print "Created Out Directory:"+directory

	width = int(320*scale)
	height = int(240*scale)
	cmaps=3
	print "Saving ... ",fileName
	filehandle=open(directory+os.sep+fileName+".txt",'w')
	filehandle.write(str(height*width*cmaps)+'\n')
	
	frames=getFrames(fileName,scale);

	out = [ (frames[i]).flatten() for i in xrange(len(frames))]
	np.savetxt(filehandle,out, fmt='%f', delimiter=' ');
	filehandle.flush();
	print "\rSaving ... ",fileName, "DONE"

if __name__ == '__main__':
	import sys
	scale=0.5
	directory="out"
	try:
		saveVideoFile(sys.argv[1],scale,directory)
	except IndexError: 
		GroundTruthFile="groundtruth.txt";
		groundTruth = getMSR2GroundTruth(GroundTruthFile);
		saveLabeledParts(scale,groundTruth,directory)
		#skipList=['1','2','15','16']
		#newskipList = [ str(x) for x in xrange(1,17) if str(x) not in skipList ]
		#saveLabeledParts(scale,groundTruth,directory,skipList=newskipList,testPer=1,valPer=0)
