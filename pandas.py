import csv
import pandas as pd
import math

# create dummy headers to be changed later   
filehead = []
for i in range(31):
    filehead.append(str(i))

# file name here
filename = "swath05FINAL.S"



# get the number of comments lines starting with 'H' and discard
file = open(filename, "r")
skip = 0
first_char = str(file.readline())[0]
skip_list = [0]
while first_char == 'H':
    skip = skip+1
    skip_list.append(skip)
    first_char = str(file.readline())[0]
print("Number of comments lines = " + str(skip))


# read file
#df1 = pd.read_csv("20230224.S",sep=' ',names=filehead)
df1 = pd.read_csv(filename,sep=' ',skiprows=skip_list,names=filehead)


# delete empty cells from df1 and rename headers
df2 = df1.dropna(axis=1,how='any')
df2.columns=['type','spl','sp','sindex','x','y','z',]



# create new attributes from string
print("****** Creating new attributes")
num_rows = len(df2.index)
num_rows = 100 # temp override num_rows to run code quickly
for i in range(num_rows):
    print(str(i) + " ",end="")
    df2.loc[i,'sindex'] = str(df2.loc[i,'sindex'])[0]
    df2.loc[i,'elev'] = str(df2.loc[i,'z'])[0:5]
    df2.loc[i,'day'] = str(df2.loc[i,'z'])[5:8]
    df2.loc[i,'h'] = str(df2.loc[i,'z'])[8:10]
    df2.loc[i,'m'] = str(df2.loc[i,'z'])[10:12]
    df2.loc[i,'s'] = str(df2.loc[i,'z'])[12:14]
    df2.loc[i,'dhms'] = str(df2.loc[i,'z'])[5:14]
    df2.loc[i,'dsd'] = str(df2.loc[i,'z'])[-7:-5]

# drop un-needed attributes
df2 = df2.drop("z", axis='columns')


# sort per time
print("Sorting on time...")
df2 = df2.sort_values('dhms')
#print(df2.to_string())

#################################
# compute "cost function"
#################################


Vel = 2100
# loop on rows
print("*** Number of lines: " + str(num_rows))
for i in range(num_rows):
    print(str(i) + " ",end="")
    ndelta_t = 0
    pdelta_t = 0
    cf = 0
    df2.loc[i,'cf'] = 0
    ##########################
    # loop on futur times
    ##########################
    j = 1
    while pdelta_t < 1000 and i+j<num_rows:
        pdelta_t = float(df2.loc[i+j,'dhms'])-float(df2.loc[i,'dhms'])
        distx = abs(float(df2.loc[i+j,'x'])-float(df2.loc[i,'x']))
        disty = abs(float(df2.loc[i+j,'y'])-float(df2.loc[i,'y']))
        dist  = math.sqrt(pow(distx,2)+pow(disty,2))
        temp_cf = 1/math.sqrt(pow(pdelta_t/1000,2)+pow(dist/Vel,2))
        if temp_cf >= cf:
            cf = temp_cf
            df2.loc[i,'dhms_cf'] = df2.loc[i+j,'dhms']
        # print("for looping i = " + str(i))
        # print("while j = " + str(j))
        # print("delta_t = " + str(pdelta_t))
        # print("cf  = " + str(temp_cf))
        j=j+1
    #print("i = " + str(i) + "***max_cf = " + str(cf))
    
    ##########################
    # loop on past times
    ##########################
    j = -1
    while ndelta_t < 1000 and i+j>0:
        ndelta_t = float(df2.loc[i+j,'dhms'])-float(df2.loc[i,'dhms'])
        distx = abs(float(df2.loc[i+j,'x'])-float(df2.loc[i,'x']))
        disty = abs(float(df2.loc[i+j,'y'])-float(df2.loc[i,'y']))
        dist  = math.sqrt(pow(distx,2)+pow(disty,2))
        temp_cf = 1/math.sqrt(pow(ndelta_t/1000,2)+pow(dist/Vel,2))
        if temp_cf >= cf:
            cf = temp_cf
            df2.loc[i,'dhms_cf'] = "-" + df2.loc[i+j,'dhms']
        # print("for looping i = " + str(i))
        # print("while j = " + str(j))
        # print("delta_t = " + str(pdelta_t))
        # print("cf  = " + str(temp_cf))
        j=j-1
    # print("i = " + str(i) + "***max_cf = " + str(cf))
    
    df2.loc[i,'cf'] = round(cf,1)
# end of loop on rows       

# print final results       
#print(df2.to_string())       

# save to new file
print("Saving new file...")
df2.to_csv('Cost_function.txt', sep='\t', index=False, encoding='utf-8')
