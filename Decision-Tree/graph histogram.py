# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 19:21:00 2016

@author: beckswu
"""
import matplotlib as plt
import csv
import operator
import numpy as np


#fr = open("","r")
data = []
label = []
first = True
i= True
a = 4 # imbalance change
number_Count = 1
with open("/Users/beckswu/Dropbox/CME practicum/Apr 22nd/ANN/Decision Tree/lag3training.csv", newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
     headline = True 
     for row in spamreader:
        if headline:
            headline = False
        else:
            row = row[0].split(",")
            temp = float(row[a])
            data.append(temp)
            number_Count += 1



with open("/Users/beckswu/Dropbox/CME practicum/Apr 22nd/ANN/Decision Tree/lag3test.csv", newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
     headline = True 
     for row in spamreader:
        if headline:
            headline = False
        else:
            row = row[0].split(",")
            temp = float(row[a])
            data.append(temp)
            number_Count += 1

print(number_Count)
"""
for r in fr.readlines():
    if first:
        first = False 
        row = r.strip().split(",")
        label = row[2:]
    else:
        row = r.strip().split(",")
        if i:
            print(row)
            i= False
        temp = float(row[a])
 """       


data.sort()
cur = data[0]
count = []
cou = 0
imba = []

count_123 = []
imba_123 =[]
imba_123.append(0)
imba_123.append(0)
for i in range(3):
    count_123.append(0)
first_threshold = int(number_Count/3)
sec_threshold = int(2*number_Count/3)
thres = [first_threshold,sec_threshold]
first = True
second = True
print(thres)
all_sum = 0

imba.append(data[0])
for i in range(len(data)):
    if cur==data[i]:
        cou+=1
        all_sum +=1 
    else:
        cur = data[i]
        imba.append(data[i])
        count.append(cou)
        if all_sum > thres[0] and first:
            first = False
            count_123[0] = all_sum-count[-1]
            print(all_sum,'  ', count[-1],'  ',imba[-2])
            imba_123[0] = imba[-3]
        elif all_sum > thres[1] and second:
            second = False
            print(all_sum,'  ', count[-1],'  ',imba[-2])
            count_123[1] = all_sum-count[-1]-count_123[0]
            imba_123[1] = imba[-3]
            count_123[2] = number_Count-count_123[0]-count_123[1]
        cou = 1
        all_sum +=1 
        

count.append(cou)
print(count_123)
print(imba_123)
print(len(count))
print(len(imba))

        
with open("lag 3 imbalance graph.csv", 'w') as csvfile:
    fieldnames = ["imbalance","amount"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(len(count)):
        writer.writerow({'imbalance': imba[i],"amount":count[i]})

#print(i)
