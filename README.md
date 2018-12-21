# Capacitated-Facility-Location-Problem
Suppose there are n facilities and m customers. 
We wish to choose:  
(1) which of the n facilities to open  
(2) the assignment of customers to facilities 
(3) The total demand assigned to a facility must not exceed its capacity. 
The objective is to minimize the sum of the opening cost and the assignment cost. 

## 算法设计与分析课程project

## 项目环境
该项目使用Windows python 3.7

## 测例数据集
题目用到的测例数据集p1到p71在Instances文件夹下

## 项目源代码
项目源代码文件只有一个，CFLP.py
该文件中实现了三个类LocalSearchSol、SimulatedAnnealingSol、TabuSearch
分别使用了局部搜索、模拟退火、禁忌搜索三种算法求解该问题

上述三个类实例化之后通过调用solve即可读入71个测例，计算出
