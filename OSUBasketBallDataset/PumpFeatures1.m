function PumpFeatures1(VideoDir,VideoName,OutDir)

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
            strcmp(cell2mat(X(j,1)),'OutDir'))
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

frames=zeros(144,256,3,numFrames);
orgFrames=read(readerobj,[1,numFrames]);

G = [0.2989,0.5870, 0.1140];

Gx = [-1 1];
Gy = Gx;


%if matlabpool('size') == 0 
%  matlabpool('open',12);
%end

for i=1:numFrames
    frame=orgFrames(:,:,:,i);
    frame=(frame(:,:,1)*G(1)+ frame(:,:,2)*G(2)+frame(:,:,3)*G(3))
    frame=imresize(frame,[144 256]);
    frame = im2double(frame);
    Ix = conv2(frame,Gx,'same');
    Iy = conv2(frame,Gy,'same');
    frames(:,:,1,i)=frame;
    frames(:,:,2,i)=Ix;
    frames(:,:,3,i)=Iy;

end

clearvars -except frames numFrames OutDir VideoDir VideoName E

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
                    images=frames(:,:,:,(startInd(i)-2):(startInd(i)+FRAME_PER_SEG-3));
                    saveToFile(FileName,images)
               end
               if ((endInd(i)-FRAME_PER_SEG+3)>0 &&(endInd(i)+2)<=numFrames)
                    %fprintf('%d:%d->%d[%d]\n',label,endInd(i)-FRAME_PER_SEG+3,endInd(i)+2,FRAME_PER_SEG);
                    images=frames(:,:,:,(endInd(i)-FRAME_PER_SEG+3):(endInd(i)+2));
                    saveToFile(FileName,images)
               end
               continue
           end
           

           
           for ind=1:FRAME_PER_SEG:(frameDuration(i)-FRAME_PER_SEG+1)
                s=ind+startInd(i)-1;
                e=s+FRAME_PER_SEG-1;
                %fprintf('%d:%d->%d[%d]\n',label,s,e,FRAME_PER_SEG);
                images=frames(:,:,:,s:e);
                saveToFile(FileName,images)
               
           end
           if (ind<frameDuration(i)-FRAME_PER_SEG+1)
                e=frameDuration(i)+startInd(i)-1;
                s=e-FRAME_PER_SEG+1;
                %fprintf('%d:%d->%d[%d]\n',label,s,e,FRAME_PER_SEG);
                images=frames(:,:,:,s:e);
                saveToFile(FileName,images)
           end
        end
    end
end

end


function saveToFile(FileName,images)
    %fprintf('%d\n', numel(images));
    outVector=double(reshape(images,1,numel(images)));
    dlmwrite(FileName,outVector,'-append','delimiter',' ');
end
