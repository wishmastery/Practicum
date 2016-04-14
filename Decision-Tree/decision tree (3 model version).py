# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 01:48:38 2016

@author: beckswu
"""

import csv
import math
import operator
import matplotlib.pyplot as plt
import numpy as np


def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet: #the the number of unique elements and their occurance
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys(): labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob *math.log(prob,2) #log base 2
    return shannonEnt
    
def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]     #chop out axis used for splitting
            reducedFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet
    
def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1      #the last column is used for the labels
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = 0
    for i in range(numFeatures):        #iterate over all the features
        featList = [example[i] for example in dataSet]#create a list of all the examples of this feature
        uniqueVals = set(featList)       #get a set of unique values
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)  
        infoGain = baseEntropy - newEntropy     #calculate the info gain; ie reduction in entropy
        if (infoGain > bestInfoGain):       #compare this to the best gain so far
            bestInfoGain = infoGain         #if better than current best, set to best
            bestFeature = i
    return bestFeature,bestInfoGain                      #returns an integer
    
    
def cal_prob(spli_data,feat):
    prob = [0,0,0]
    for i in range(len(spli_data)):
        if spli_data[i][feat] == 0:
            prob[0]+=1
        if spli_data[i][feat] == 1:
            prob[1]+=1
        if spli_data[i][feat] == -1:
            prob[2]+=1
    prob = [key/len(spli_data) for key in prob]
    return prob

def majorityCnt(classList):
    classCount={}
    for vote in classList:
        if vote not in classCount.keys(): classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def createTree(dataSet,labels,best_gain,info_list,pro_list):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList): 
        return classList[0],best_gain,info_list,pro_list#stop splitting when all of the classes are equal
    if len(dataSet[0]) == 1: #stop splitting when there are no more features in dataSet
        return majorityCnt(classList),best_gain,info_list,pro_list
    bestFeat, gain = chooseBestFeatureToSplit(dataSet)
    best_gain += gain
    bestFeatLabel = labels[bestFeat]
    prob= cal_prob(dataSet,bestFeat)
    pro_list.append([bestFeatLabel,prob])
    info_list.append([bestFeatLabel,gain])
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]       #copy all of labels, so trees don't mess up existing labels
        myTree[bestFeatLabel][value],best_gain,info_list,prob_list = createTree(splitDataSet(dataSet, bestFeat, value),subLabels,best_gain,info_list,pro_list)
    return myTree,best_gain ,info_list ,pro_list          
    
def classify(inputTree,featLabels,testVec):
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    key = testVec[featIndex]
    valueOfFeat = secondDict[key]
    if isinstance(valueOfFeat, dict): 
        classLabel = classify(valueOfFeat, featLabels, testVec)
    else: classLabel = valueOfFeat
    return classLabel

    
def createDataSet(filename):
    with open(filename, newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
     headline = True 
     data = []
     for row in spamreader:
        if headline:
            headline = False
        else:
            temp1 = [key for key in row[0].split(",")] 
            temp2 = [int(key) for key in temp1[0:4]]
            #temp2.append(int(temp1[4]))
            if temp1[-1] == "1":
                temp2.append("U")
            if temp1[-1] == "-1":
               temp2.append("D")
            if temp1[-1] == "0":
               temp2.append("N")
            data.append(temp2)
     my_labels = ["I4","V4","I3","V3"]#,\
     #"I2","V2","I1","V1","bid","ask","Imba","WP","vol","imba value", "vol imba value","direction"]
     return data, my_labels
  
def createDataSet1(filename):
    with open(filename, newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
     headline = True 
     data = []
     for row in spamreader:
        if headline:
            headline = False
        else:
            temp1 = [key for key in row[0].split(",")] 
            temp2 = [int(key) for key in temp1[0:4]]
            if temp1[-1] == "1":
                temp2.append("U")
            if temp1[-1] == "0":
               temp2.append("D")
            data.append(temp2)
     my_labels = ["I4","V4","I3","V3"]#,\
     #"I2","V2","I1","V1","bid","ask","Imba","WP","vol","imba value", "vol imba value","direction"]
     return data, my_labels
  
def autolabel(rects,ax):
        # attach some text labels
    for rect in rects:
         height = rect.get_height()
         ax.text(rect.get_x() + rect.get_width()/2., 1.0001*height,\
         '%f' % height,ha='center', va='bottom')
    
def graph(N,gain):    
    ind = np.arange(N)  # the x locations for the groups
    width = 0.40      # the width of the bars
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, gain, width, color='r')
    
    # add some text for labels, title and axes ticks
    ax.set_ylabel('infogain')
    ax.set_title('Compare total info gain for each result')
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(('SVM','ANN'))
 
    autolabel(rects1,ax)
    plt.show()
    
def getNumLeafs(myTree):
    numLeafs = 0
    firstStr = list(myTree.keys())[0]
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        if type(secondDict[key]) == dict:#test to see if the nodes are dictonaires, if not they are leaf nodes
            numLeafs += getNumLeafs(secondDict[key])
        else:   numLeafs +=1
    return numLeafs

def getTreeDepth(myTree):
    maxDepth = 0
    firstStr = list(myTree.keys())[0]
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        if type(secondDict[key]) == dict :#test to see if the nodes are dictonaires, if not they are leaf nodes
            thisDepth = 1 + getTreeDepth(secondDict[key])
        else:   thisDepth = 1
        if thisDepth > maxDepth: maxDepth = thisDepth
    return maxDepth

def plotNode(nodeTxt, centerPt, parentPt, nodeType):
    createPlot.ax1.annotate(nodeTxt, xy=parentPt,  xycoords='axes fraction',
             xytext=centerPt, textcoords='axes fraction',
             va="center", ha="center", bbox=nodeType, arrowprops=arrow_args )
    
def plotMidText(cntrPt, parentPt, txtString):
    xMid = (parentPt[0]-cntrPt[0])/2.0 + cntrPt[0]
    yMid = (parentPt[1]-cntrPt[1])/2.0 + cntrPt[1]
    createPlot.ax1.text(xMid, yMid, txtString, va="center", ha="center", \
    rotation=30)

def plotTree(myTree, parentPt, nodeTxt):#if the first key tells you what feat was split on
    numLeafs = getNumLeafs(myTree)  #this determines the x width of this tree
    depth = getTreeDepth(myTree)
    firstStr = list(myTree.keys())[0]     #the text label for this node should be this
    cntrPt = (plotTree.xOff + (1.0 + float(numLeafs))/2.0/plotTree.totalW, \
    plotTree.yOff)
    plotMidText(cntrPt, parentPt, nodeTxt)
    plotNode(firstStr, cntrPt, parentPt, decisionNode)
    secondDict = myTree[firstStr]
    plotTree.yOff = plotTree.yOff - 1.0/plotTree.totalD
    for key in secondDict.keys():
        if type(secondDict[key]) is dict:#test to see if the nodes are dictonaires, if not they are leaf nodes   
            plotTree(secondDict[key],cntrPt,str(key))        #recursion
        else:   #it's a leaf node print the leaf node
            plotTree.xOff = plotTree.xOff + 1.0/plotTree.totalW
            plotNode(secondDict[key], (plotTree.xOff, plotTree.yOff), cntrPt, \
            leafNode)
            plotMidText((plotTree.xOff, plotTree.yOff), cntrPt, str(key))
    plotTree.yOff = plotTree.yOff + 1.0/plotTree.totalD
#if you do get a dictonary you know it's a tree, and the first element will be another dict

def createPlot(inTree):
    fig = plt.figure(1, facecolor='white')
    fig.clf()
    axprops = dict(xticks=[], yticks=[])
    createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)    #no ticks
    #createPlot.ax1 = plt.subplot(111, frameon=False) #ticks for demo puropses 
    plotTree.totalW = float(getNumLeafs(inTree))
    plotTree.totalD = float(getTreeDepth(inTree))
    plotTree.xOff = -0.5/plotTree.totalW; plotTree.yOff = 1.0;
    plotTree(inTree, (0.5,1.0), '')
    plt.show()


if __name__=='__main__':
    csv_set = ["/Users/beckswu/Dropbox/CME practicum/Apr 8st/SVM/svm.csv",\
    "/Users/beckswu/Dropbox/CME practicum/Apr 8st/ANN/ann.csv"]
    gain=[]
    for i in range(len(csv_set)):
        if i==1:
            dataset, labels = createDataSet1(csv_set[i])
            dataset = dataset[-11397:]
        else:
            dataset, labels = createDataSet(csv_set[i])
       #calculate the ratio:
        print(len(dataset))
        best_gain = 0.0
        probability_list = []
        info_list = []
        tree,infogain,info_list,probability_list = createTree(dataset,labels,best_gain,info_list,probability_list)
        print("\n",tree,"\n")
        gain.append(infogain)
        print("total infogain :  ",infogain,'\n')
        print("Infomation Gain At Each Node: \n")
        print(info_list)
        print("\n")
        print("probability At Each Node: \n")
        print(probability_list)
        print("\n")
        decisionNode = dict(boxstyle = "sawtooth",fc='0.8')
        leafNode = dict(boxstyle='round4',fc='0.8')
        arrow_args = dict(arrowstyle="<-")
        createPlot(tree)
        print("I4: Volume imbalance lag 4, V4: volume lag 4, I3:Volume imbalance lag 4, V3: volume lag 3")
                
    
    graph(len(csv_set),gain)
