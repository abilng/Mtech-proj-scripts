#! /usr/bin/env python2.7
import numpy as np
import cv2
import os
import random
from numpy import cumsum


def getGroundTruth(GroundTruthFile):
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

def getFrames(File,scale):
	cap = cv2.VideoCapture(File)
	cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,0)

	framecount = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)*scale)
	height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)*scale)

	frames = np.zeros((framecount,height,width,3));

	count = 0
	while True:
		ret, frame = cap.read()
		if not ret:
			 break
		frame = cv2.resize(frame,None, fx=scale, fy=scale, interpolation = cv2.INTER_LINEAR)
		frames[count] = (frame/float(255))
		count+=1
	cap.release()
	print frames.shape
	return frames



scale=0.5
directory="out"
GroundTruthFile="groundtruth.txt";
labelNames=["clapping","waving","boxing"]
length=5

testPer=0.1
valPer=0.1
trainPer = 1-(testPer+valPer);

groundTruth = getGroundTruth(GroundTruthFile);

if not os.path.exists(directory): os.mkdir(directory)
print "Created Out Directory:"+directory


trainFiles= [ open(directory+os.sep+name+"_train.txt",'w') for name in labelNames]
testFiles= [ open(directory+os.sep+name+"_test.txt",'w') for name in labelNames]
valFiles= [ open(directory+os.sep+name+"_val.txt",'w') for name in labelNames]

width = int(320*scale)
height = int(240*scale)
cmaps=3

for f in trainFiles: f.write(str(height*width*length*cmaps)+'\n')
for f in testFiles: f.write(str(height*width*length*cmaps)+'\n')
for f in valFiles: f.write(str(height*width*length*cmaps)+'\n')

for (fileName,labels) in groundTruth.items():
	frames=getFrames(fileName+".avi",scale);
	for label in labels:
		#print label,label['length']+label['start']
		ind = [i for i in xrange(label['start']+length,label['length']+label['start'],length)]
		random.shuffle(ind)
		stops=map(int, cumsum([trainPer,testPer,valPer])*len(ind));
		trainInd,testInd,valInd = [ind[a:b] for a, b in zip([0]+stops, stops)];

		filehandle = trainFiles[label['action']-1]
		out = [ (frames[end-length:end]).flatten() for end in trainInd]
		np.savetxt(filehandle,out, fmt='%f', delimiter=' ');
		filehandle.flush();

		filehandle = testFiles[label['action']-1]
		out = [ (frames[end-length:end]).flatten() for end in testInd]
		np.savetxt(filehandle,out, fmt='%f', delimiter=' ');
		filehandle.flush();

		filehandle = valFiles[label['action']-1]
		out = [ (frames[end-length:end]).flatten() for end in valInd]
		np.savetxt(filehandle,out, fmt='%f', delimiter=' ');
		filehandle.flush();
	#for labels

print frames[-length:].shape