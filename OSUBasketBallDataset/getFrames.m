function getFrames(VideoDir,VideoName,OutDir)
%getFrames get (Gray,Edge,FrameDiff) of each frame.
%   get (Gray,Edge,FrameDiff) of each frame.

readerobj = VideoReader([ VideoDir '/' VideoName ],'tag', 'myreader1');
numFrames = get(readerobj, 'numberOfFrames');

frames=zeros(numFrames,144,256,3);
orgFrames=zeros(144,256,numFrames);

G = [0.2989,0.5870, 0.1140];

for i=1:numFrames
	frame = read(readerobj,i);
	frame = (frame(:,:,1)*G(1)+ frame(:,:,2)*G(2)+frame(:,:,3)*G(3));
	frame = imresize(frame,[144 256]);
	orgFrames(:,:,i) = frame;
end


%if matlabpool('size') == 0 
%  matlabpool('open',12);
%end

for i=1:numFrames
	frame=orgFrames(:,:,i);
	Edge = edge(frame,'canny');

	frames(i,:,:,1)=im2double(frame);
	frames(i,:,:,2)=im2double(Edge);
	if i==1
		frames(i,:,:,3)=im2double(Edge);
	else
		frames(i,:,:,3)=im2double(imabsdiff(orgFrames(:,:,i),orgFrames(:,:,i-1)));
	end

end

frames=double(reshape(frames,numFrames,144*256*3))./255;

clearvars -except frames numFrames OutDir VideoDir VideoName

DirName=[OutDir '/' VideoDir '/' VideoName(end-4)];
mkdir(DirName)

%if matlabpool('size') == 0 
%  matlabpool('open',12);
%end

FileName=[DirName '/' VideoName '.txt'];
fprintf('Opening %s.....\n',FileName);
fclose(fopen(FileName, 'w'));
dlmwrite(FileName,frames(Indexes,:),'-append','delimiter',' ');	

end

