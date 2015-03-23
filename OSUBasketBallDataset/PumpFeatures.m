function PumpFeatures(VideoDir,VideoName,OutDir,RandomFrames,Grey)

if nargin < 4
   RandomFrames = true
end
if nargin < 5
   Grey = false
end
load([ VideoDir '/' VideoName(end-4) '.mat'])
X=who;

%
%    I=read(readerobj,i);
%    imshow(I)
%    hold on
E=cell(size(X,1)-3,1);
i=1;
for j=1:size(X,1)
    if(strcmp(cell2mat(X(j,1)),'Lab1')|| ...
            strcmp(cell2mat(X(j,1)),'VideoName')|| ...
            strcmp(cell2mat(X(j,1)),'VideoDir')|| ...
            strcmp(cell2mat(X(j,1)),'OutDir') || ...
            strcmp(cell2mat(X(j,1)),'Grey') || ...
            strcmp(cell2mat(X(j,1)),'RandomFrames'))
        continue;
    else
        eval(['FinalLocations=' cell2mat(X(j,1)) ';']);
        A=FinalLocations(5,:);
        A(A==11)=0;
        E{i}=A;
        i=i+1;
    end
end
E=cell2mat(E);

Pri= zeros(1,10);
for i=1:10
    Pri(i)=sum(sum(E==i))/size(A,2);
end

disp(Pri);

readerobj = VideoReader([ VideoDir '/' VideoName ],'tag', 'myreader1');
numFrames = get(readerobj, 'numberOfFrames');
if (Grey)
    frames=zeros(144,256,numFrames);
else 
    frames=zeros(144,256,3,numFrames);
end
orgFrames=read(readerobj,[1,numFrames]);

%if matlabpool('size') == 0 
%  matlabpool('open',12);
%end
for i=1:numFrames
    %frame=read(readerobj,i);
    frame=orgFrames(:,:,:,i);
    if (Grey)
        frame=rgb2gray(frame);
        frame=imresize(frame,[144 256]);
        frames(:,:,i)=frame;
    else
        frame=imresize(frame,[144 256]);
        frames(:,:,:,i)=frame;
    end
end

clearvars -except frames numFrames OutDir VideoDir VideoName E RandomFrames Grey

labelNames={'Dribbling','Jumping','Shooting','Passing','Catching',...
    'HoldingBall','Bouncing','BallTrajectory','BallContact','NearRim'};
FRAME_PER_SEG=5;

DirName=[OutDir '/' VideoDir '/' VideoName(end-4)];
mkdir(DirName)


%if matlabpool('size') == 0 
%  matlabpool('open',12);
%end
for label=1:10
    FileName=[DirName '/' labelNames{label} '.txt'];
    fprintf('Opening %s.....\n',FileName);
    fclose(fopen(FileName, 'w'));
%end
%parfor label=1:10
%    FileName=[DirName '/' labelNames{label} '.txt'];
    for event=1:size(E,1)
        Indexes=(E(event,:)==label);
        if (~any(Indexes))
            fprintf('Skiping Label %d on %d\n',label,event);
            continue;
        end;
        startInd=find(diff([0,Indexes])==1);
        endInd=find(diff([Indexes,0])==-1);
        frameDuration=endInd-startInd+1;
        for i=1:size(frameDuration,2)
           %load Frames
           %fprintf('Found Label:%d(%d) %d frames from %d to %d\n',label,event,frameDuration(i),startInd(i),endInd(i));
           if(frameDuration(i)<FRAME_PER_SEG)
               if((startInd(i)-2)>0 &&(startInd(i)+FRAME_PER_SEG-3)<=numFrames)
                    %fprintf('%d:%d->%d[%d]\n',label,startInd(i)-2,startInd(i)+FRAME_PER_SEG-3,FRAME_PER_SEG);
                    if (Grey)
                        images=frames(:,:,(startInd(i)-2):(startInd(i)+FRAME_PER_SEG-3));
                    else
                        images=frames(:,:,:,(startInd(i)-2):(startInd(i)+FRAME_PER_SEG-3));
                    end
                    saveToFile(FileName,images)
               end
               if ((endInd(i)-FRAME_PER_SEG+3)>0 &&(endInd(i)+2)<=numFrames)
                    %fprintf('%d:%d->%d[%d]\n',label,endInd(i)-FRAME_PER_SEG+3,endInd(i)+2,FRAME_PER_SEG);
                    if (Grey)
                        images=frames(:,:,(endInd(i)-FRAME_PER_SEG+3):(endInd(i)+2));
                    else
                        images=frames(:,:,:,(endInd(i)-FRAME_PER_SEG+3):(endInd(i)+2));
                    end
                    saveToFile(FileName,images)
               end
               continue
           end
           

           
           for ind=1:FRAME_PER_SEG:(frameDuration(i)-FRAME_PER_SEG+1)
                s=ind+startInd(i)-1;
                e=s+FRAME_PER_SEG-1;
                %fprintf('%d:%d->%d[%d]\n',label,s,e,FRAME_PER_SEG);
                if (Grey)
                    images=frames(:,:,s:e);
                else
                    images=frames(:,:,:,s:e);
                end
                saveToFile(FileName,images)
               
           end
           if (ind<frameDuration(i)-FRAME_PER_SEG+1)
                e=frameDuration(i)+startInd(i)-1;
                s=e-FRAME_PER_SEG+1;
                %fprintf('%d:%d->%d[%d]\n',label,s,e,FRAME_PER_SEG);
                if (Grey)
                    images=frames(:,:,s:e);
                else
                    images=frames(:,:,:,s:e);
                end
                saveToFile(FileName,images)
           end
           if (RandomFrames)
               stepSize=2*FRAME_PER_SEG;
               while( floor(frameDuration(i)/(stepSize)) >0)
                   for ind=1:stepSize:(frameDuration(i)-stepSize+1)
                        I=sort(randperm(stepSize,FRAME_PER_SEG))+(ind-1)+(startInd(i)-1);
                        %fprintf('%d:rnd %d---%d [%d] %d\n',label,I(1),I(10),FRAME_PER_SEG,stepSize);
                        if (Grey)
                            images=frames(:,:,I);
                        else
                            images=frames(:,:,:,I);
                        end
                        saveToFile(FileName,images)
                   end
                   if(ind<frameDuration(i)-stepSize+1)
                        I=sort(randperm(stepSize,FRAME_PER_SEG))+ ...
                           (frameDuration(i)-stepSize)+(startInd(i)-1);
                        %fprintf('%d:rnd %d---%d [%d] %d\n',label,I(1),I(10),FRAME_PER_SEG,stepSize);
                        if (Grey)
                            images=frames(:,:,I);
                        else
                            images=frames(:,:,:,I);
                        end
                        saveToFile(FileName,images)
                   end
                   stepSize=stepSize*2;
               end
           end
        end
    end
end
end


function saveToFile(FileName,images)
    %fprintf('%d\n', numel(images));
    outVector=double(reshape(images,1,numel(images)))./256;
    dlmwrite(FileName,outVector,'-append','delimiter',' ');
end
