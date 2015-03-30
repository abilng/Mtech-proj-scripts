import numpy as np
import cv2

def draw_str(dst, (x, y), s):
	cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
	cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.CV_AA)

def main(videofile,labelfile):

	fileptr = open(labelfile,'r');
	labels =[ int(x[0]) for x in fileptr.readlines() ]
	labelNames=["boxing","clapping","waving"]

	cap = cv2.VideoCapture(videofile)
	cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,0)
	fps = int(cap.get(cv2.cv.CV_CAP_PROP_FPS));
	N = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

	print("No of Frames        : "+ str(N));
	print("Original Width      : " +str(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))); 
	print("Original Height     : " +str(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)));
	print("Original FrameRate  : " +str(fps));
	i=0;
	while True:
		ret, img = cap.read()
		print 'Playing ....................... [{0}%]\r'.format((i*100/N)),
		if not ret:
			break

		draw_str(img, (20, 20), "label     :  " + labelNames[labels[i]])
		cv2.imshow('video', img)
		i+=1
		ch = 0xFF & cv2.waitKey(1000/(fps+1))
		if ch == ord('q') or ch == 27:
			break
	cap.release()
	print('Playing ....................... [STOP]')
	cv2.destroyAllWindows()

if __name__ == '__main__':
	import sys
	main(sys.argv[1],sys.argv[2])