#! /usr/bin/env python2.7
import numpy as np
import cv2
import os
from multiprocessing.pool import ThreadPool
from collections import deque


scale=0.5
directory="out"


GroundTruthFile="groundtruth.txt";
labels = {}
labelNames=["clapping","waving","boxing"]

if not os.path.exists(directory): os.mkdir(directory)
print "Created Out Directory:"+directory

height=320*scale
width=240*scale
length=5


threadn = cv2.getNumberOfCPUs()
pool = ThreadPool(processes = threadn)
pending = deque()


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


outFiles= [ open(directory+os.sep+name+".txt",'w') for name in labelNames]

for f in outFiles: f.write(str(height*width*length)+'\n')
    
    
def process_frame(frame, count):
    # some intensive computation...
    frame = cv2.resize(frame,None, fx=scale, fy=scale, interpolation = cv2.INTER_LINEAR)
    return (frame/float(255)),count

for (key,val) in labels.items():
    cap = cv2.VideoCapture( key+'.avi')
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,0)
    
    framecount = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    frames = np.zeros((framecount,width,height,3));

        #frames[count]=frame/float(255);
    count = 0
    while True:
        if len(pending) < threadn:
            ret, frame = cap.read()
            if ret:        
                task = pool.apply_async(process_frame, (frame.copy(), count))
                pending.append(task)
                count+=1
            else:
                if(len(pending)==0): break;

        while len(pending) > 0 and pending[0].ready():
            res, t0 = pending.popleft().get()
            frames[t0]=res;

    print frames.shape
