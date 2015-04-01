import os,random
from numpy import cumsum

def appendData(labelNames,inputfilemap,directory,dim,testPer=0.1,valPer=0.1):
	trainPer = 1-(testPer+valPer);
		
	if not os.path.exists(directory): os.mkdir(directory)
	print "Created Out Directory:"+directory

	trainFiles= [ open(directory+os.sep+name+"_train.txt",'w') for name in labelNames]
	testFiles= [ open(directory+os.sep+name+"_test.txt",'w') for name in labelNames]
	valFiles= [ open(directory+os.sep+name+"_val.txt",'w') for name in labelNames]

	for f in trainFiles: f.write(str(dim)+'\n')
	for f in testFiles: f.write(str(dim)+'\n')
	for f in valFiles: f.write(str(dim)+'\n')

	for labelNo in xrange(len(labelNames)):
		for infile in inputfilemap[labelNo]:
			print 'for label ', labelNames[labelNo], ' file: ', infile
			fp = open(infile,'rb');
			data = fp.readlines();
			if len(data) == 0:
				continue
			ind = [i for i in xrange(len(data))]
			random.shuffle(ind)
			stops=map(int, cumsum([trainPer,testPer,valPer])*len(ind));
			trainInd,testInd,valInd = [ind[a:b] for a, b in zip([0]+stops, stops)];

			filehandle = trainFiles[labelNo]
			out = [ data[i] for i in trainInd]
			filehandle.writelines(out);
			filehandle.flush();
	
			filehandle = testFiles[labelNo]
			out = [ data[i] for i in testInd]
			filehandle.writelines(out);
			filehandle.flush();
	
			filehandle = valFiles[labelNo]
			out = [ data[i] for i in valInd]
			filehandle.writelines(out);
			filehandle.flush();

if __name__ == '__main__':

	labelNames = ["Passing","Catching","HoldingBall","Shooting","Jumping","Dribbling","BallTrajectory","BallContact","Bouncing","NearRim"]

	inputfilemap = [
	["TwoOnTwo/3/Passing.txt", "TwoOnTwo/4/Passing.txt", "TwoOnTwo/5/Passing.txt", "TwoOnTwo/7/Passing.txt"],
	["TwoOnTwo/3/Catching.txt", "TwoOnTwo/4/Catching.txt", "TwoOnTwo/5/Catching.txt", "TwoOnTwo/7/Catching.txt"],
	["TwoOnTwo/3/HoldingBall.txt", "TwoOnTwo/4/HoldingBall.txt", "TwoOnTwo/5/HoldingBall.txt", "TwoOnTwo/7/HoldingBall.txt"],
	["TwoOnTwo/3/Shooting.txt", "TwoOnTwo/4/Shooting.txt", "TwoOnTwo/5/Shooting.txt", "TwoOnTwo/7/Shooting.txt"],
	["TwoOnTwo/3/Jumping.txt", "TwoOnTwo/4/Jumping.txt", "TwoOnTwo/5/Jumping.txt", "TwoOnTwo/7/Jumping.txt"],
	["TwoOnTwo/3/Dribbling.txt", "TwoOnTwo/4/Dribbling.txt", "TwoOnTwo/5/Dribbling.txt", "TwoOnTwo/7/Dribbling.txt"],
	["TwoOnTwo/3/BallTrajectory.txt", "TwoOnTwo/4/BallTrajectory.txt", "TwoOnTwo/5/BallTrajectory.txt", "TwoOnTwo/7/BallTrajectory.txt"],
	["TwoOnTwo/3/BallContact.txt", "TwoOnTwo/4/BallContact.txt", "TwoOnTwo/5/BallContact.txt", "TwoOnTwo/7/BallContact.txt"],
	["TwoOnTwo/3/Bouncing.txt", "TwoOnTwo/4/Bouncing.txt", "TwoOnTwo/5/Bouncing.txt", "TwoOnTwo/7/Bouncing.txt"],
	["TwoOnTwo/3/NearRim.txt", "TwoOnTwo/4/NearRim.txt", "TwoOnTwo/5/NearRim.txt", "TwoOnTwo/7/NearRim.txt"]
	]

	appendData(labelNames,inputfilemap,'data',3*144*256,testPer=0.1,valPer=0.1);