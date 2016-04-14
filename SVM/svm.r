setwd("/Users/lyujianoliver/Desktop")
library(e1071)

convert=function(x)
{
  ifelse(x>0,1,ifelse(x<0,-1,0))
}

rounddata=function(data)
{
  for(i in 1:ncol(data))
  {
    data[,i]=round(data[,i],2)
  }
  data
}


filter_data=function(data)
{
  data[,ncol(data)]=c(diff(data[,ncol(data)]),0)
  data=data[data[,ncol(data)]!=0,]
  data[,ncol(data)]=convert(data[,ncol(data)])
  data
}

decision_tree=function(data)
{
  for(i in 1:(ncol(data)-2))
  {
    data[,i]=convert(data[,i])
  }
  data
}

run_svm=function(datadata)
{
  
  b=datadata[,ncol(datadata)];
  b=as.factor(b);
  percent80=round(0.8*nrow(datadata));
  percent20=nrow(datadata)-percent80;
  x=datadata[1:percent80,2:(ncol(datadata)-1)];
  y=b[1:percent80];
  model=svm(x,y,kernel="radial");
  testing=datadata[percent80:nrow(datadata),2:(ncol(datadata)-1)];
  real=b[percent80:length(b)];
  pred=predict(model,testing);
  a=list();
  a[[1]]=table(real,pred);
  a[[2]]=data.frame(testing,real,pred);
  a[[3]]=decision_tree(a[[2]]);
  a
}

data0 <-read.table("withoutBookRec.txt",sep=",",header=TRUE)
data1 <-read.table("with1BookRec.txt",sep=",",header=TRUE)
data3 <-read.table("with3BookRec.txt",sep=",",header=TRUE)
data5 <-read.table("with5BookRec.txt",sep=",",header=TRUE)

data0=rounddata(data0)
data1=rounddata(data1)
data3=rounddata(data3)
data5=rounddata(data5)


data0=filter_data(data0)
data1=filter_data(data1)
data3=filter_data(data3)
data5=filter_data(data5)

data0=data0[,-ncol(data0)]
data1=data1[,-ncol(data1)]
data3=data3[,-ncol(data3)]
data5=data5[,-ncol(data5)]


result0=run_svm(data0)
result1=run_svm(data1)
result3=run_svm(data3)
result5=run_svm(data5)

write.csv(result0[[3]],"with0_decision_tree.csv",row.names=FALSE)
write.csv(result1[[3]],"with1_decision_tree.csv",row.names=FALSE)
write.csv(result3[[3]],"with3_decision_tree.csv",row.names=FALSE)
write.csv(result5[[3]],"with5_decision_tree.csv",row.names=FALSE)

write.csv(result0[[2]],"with0_testing_data.csv",row.names=FALSE)
write.csv(result1[[2]],"with1_testing_data.csv",row.names=FALSE)
write.csv(result3[[2]],"with3_testing_data.csv",row.names=FALSE)
write.csv(result5[[2]],"with5_testing_data.csv",row.names=FALSE)
