function getLabeledMaskedFrames(VideoDir,VideoName,OutDir,OutDir1)
%getFrames get (Gray,Edge,FrameDiff) of each frame.
%   get (Gray,Edge,FrameDiff) of each frame.

load([ VideoDir '/' VideoName(end-4) '.mat']);
X=who;

if(nargin<4)
	OutDir1 = '';
end

%
%	I=read(readerobj,i);
%	imshow(I)
%	hold on
E=cell(size(X,1)-3,1);
E_boder=cell(size(X,1)-3,1);
i=1;
for j=1:size(X,1)
	if(strcmp(cell2mat(X(j,1)),'Lab1')|| ...
			strcmp(cell2mat(X(j,1)),'VideoName')|| ...
			strcmp(cell2mat(X(j,1)),'VideoDir')|| ...
			strcmp(cell2mat(X(j,1)),'OutDir')|| ...
			strcmp(cell2mat(X(j,1)),'OutDir1'))
		continue;
	else
		eval(['FinalLocations=' cell2mat(X(j,1)) ';']);
		A=FinalLocations(5,:);
		A(A==11)=0;
		E{i}=A;
        B=FinalLocations(1:4,:)';
        %[x,y,w,h]
        B(:,3)= B(:,3)+B(:,1); 
        B(:,4)= B(:,4)+B(:,2);
        B(:,1)=round(B(:,1)*(256/960));
        B(:,2)=round(B(:,2)*(144/540));
        B(:,3)=round(B(:,3)*(256/960));
        B(:,4)=round(B(:,4)*(144/540));

        B(B(:,1)<1,1)=1;
        B(B(:,2)<1,2)=1;
        B(B(:,3)>256,3)=256;
        B(B(:,4)>144,4)=144;
        
        E_boder{i}=B;
		i=i+1;
	end
end
E=cell2mat(E);


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

clearvars -except frames numFrames OutDir VideoDir VideoName E OutDir1 E_boder

%frames=double(reshape(frames,numFrames,144*256*3))./255;

labelNames={'Dribbling','Jumping','Shooting','Passing','Catching',...
	'HoldingBall','Bouncing','BallTrajectory','BallContact','NearRim'};

DirName=[OutDir '/' VideoDir '/' VideoName(end-4)];
mkdir(DirName)

%if matlabpool('size') == 0 
%  matlabpool('open',12);
%end

for label=1:10
	FileName=[DirName '/' labelNames{label} '.txt'];
	fprintf('Opening %s.....\n',FileName);
	fclose(fopen(FileName, 'w'));
	for event=1:size(E,1)
		Indexes=(E(event,:)==label);
		%E(Indexes,:)
		if (~any(Indexes))
			fprintf('Skiping Label %d on %d\n',label,event);
			continue;
		end;
        outMat = zeros(144,256,3);
        B=E_boder{event};
        %disp(event);
        for ind=find(Indexes)
            outMat(:) = 0;
            outMat(B(ind,2):B(ind,4),B(ind,1):B(ind,3),:) ...
                = frames(ind,B(ind,2):B(ind,4),B(ind,1):B(ind,3),:);
            outVector = double(reshape(outMat,1,144*256*3))./255;
            dlmwrite(FileName,outVector,'-append','delimiter',' ', ...
                'precision',3);
            %disp(ind);
        end
	end
end

if (~isempty(OutDir1))
	DirName=[OutDir1 '/' VideoDir '/' VideoName(end-4)];
	mkdir(DirName)
	FileName=[DirName '/' VideoName '.txt'];
	fprintf('Opening %s.....\n',FileName);
	fclose(fopen(FileName, 'w'));
	dlmwrite(FileName,frames,'-append','delimiter',' ','precision',3);
end

end

