# Gilbert Velasquez 
# CS 4390: Information Retrieval and Visualization  
# This program extracts relevant information from the UTEP CS Department's Faculty page, and saves it as a pkl file. It also creates text documents and ranks them based on how many times a target word is found within them
# 
# Change Log:   11/12/2020  constructProfessorsPD() implemented
#               11/16/2020  createWebsiteTextFiles() and getUserName() implemented. Path updated to store txt files into Professors folder
#               11/17/2020  createListOfFiles() , countWordOccurrences() , createRankingOutput() , and getFirstWord() implemented 
#               11/18/2020  added time to allow user to see how long each query takes to rank. Spellcheck and Spacing clean up 

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import pickle
import sys
import os
import shutil
import time


#### This Method Constructs the Professors Panda Dataframe
def constructProfessorsPD():
    req = requests.get('https://www.utep.edu/cs/people/index.html') # Provded Website 
    soup = BeautifulSoup(req.text,'lxml')
    divs = soup.findAll("div",{"class":"col-md-6"}) # returns an array contianing all information of th

    temp = []
    for div in divs:
        facultyTitle = div.find('span',{"class":"Title"})
        if facultyTitle is not None: # check the contents arent empty
            if "Professor" in facultyTitle.text: # print only the professors
                tempTitle = facultyTitle.text
            
                facultyName = div.find('h3', {"class":"name"})
                if facultyName is not None: # check the contents arent empty
                    tempName = facultyName.text
                else:
                    tempName = "NONE"

                facultyEmail = div.find('span',{"class":"email"})
                if facultyEmail is not None: # check the contents arent empty
                    tempEmail = facultyEmail.text
                else:
                    tempEmail = "NONE"

                facultyAddress = div.find('span', {"class":"address"})
                if facultyAddress is not None: # check the contents arent empty
                    tempAddress = facultyAddress.text
                else:
                    tempAddress = "NONE"

                facultyPhone = div.find('span', {"class" : "phone"})
                if facultyPhone is not None:
                    tempPhone = facultyPhone.text
                    tempPhone = tempPhone[0:13] # filter so we only get the phone number
                else:
                    tempPhone = "NONE"


                facultyWebPage = div.findAll('a')
                facultyURL = facultyWebPage[len(facultyWebPage)-1].get("href")
                if facultyWebPage is not None and len(facultyURL) > 0:
                    tempURL = facultyURL 

                else:
                    tempURL = "NONE"

                temp.append([tempName,tempTitle,tempAddress,tempEmail,tempPhone,tempURL])

    dfColumns = ["Name","Title","Office","Email","Phone","Website"]
    data = np.array(temp)
    Professors = pd.DataFrame(data, columns = dfColumns)

    return Professors

# This Method will create the Professors Folder and store the txt files containg the information from each professors Website
def createWebsiteTextFiles(Professors,path):
    os.chdir(path)
    pathToAppend = "./professors"

    if os.path.exists(pathToAppend): # remove the folder if it is already there, so we dont encounter errors 
        shutil.rmtree(pathToAppend)
        os.mkdir(pathToAppend)
    else:
        os.mkdir(pathToAppend) # create the folder if not 

    urlList = [] 
    emailAndWebsiteList = Professors[["Email","Website"]]
    emailAndWebsiteList = emailAndWebsiteList.values.tolist()

    usernameAndWebsiteList = []
    for emailAndWebsite in emailAndWebsiteList:
        username = getUserName(emailAndWebsite[0])
        usernameAndWebsiteList.append([username,emailAndWebsite[1]])


    for website in usernameAndWebsiteList:
        if(website[1] != "NONE"):
            webPageContent = requests.get(website[1])
            content = (BeautifulSoup(webPageContent.text, "lxml"))
            stringContent = str(content.text)

            filename = website[0] + ".txt"
            fileLocationName = os.path.join(pathToAppend,filename)
            f = open(fileLocationName,'w', encoding = "utf-8")
            f.write(stringContent)

# This method will pull out the username from an Email 
def getUserName(email):
    i = 0
    while email[i] != "@":
        i +=1
    return email[0:i]



# ***************************** Part 2 Methods ***************************** 

# This method will store all the files in the professors folder into a List 
def createListOfFiles(path):
    os.chdir(path)
    pathToAppend = "./professors"
    files = []
    for fileName in os.listdir(pathToAppend):
        if fileName.endswith('.txt'):
            files.append(fileName)
    return files 

# This method will count all the occurences of a word in every file in the files list 
def countWordOccurrences(files,target,path):
    os.chdir(path+"/professors")

    wordOccurrencesAndFileName = []

    for fileName in files:
        count = 0
        f = open(fileName,'r', encoding= "utf-8")
        for line in f.readlines():
            for word in line.split():
                if word.lower() == target.lower():
                    count = count + 1
        wordOccurrencesAndFileName.append([fileName,count])
        wordOccurrencesAndFileName = sorted(wordOccurrencesAndFileName,key = lambda x:x[1], reverse = True)

    return wordOccurrencesAndFileName

# This method will output the query results based on the given format 
def createRankingOutput(wordOccurrencesAndFileName,Professors,target):
    trashChars = "\'[]" # charaters we dont want to see in our strings 
    rank = 1
    for ranking in wordOccurrencesAndFileName:
        username = ranking[0][:len(ranking[0]) - 4]
        if username =="longpre": # There is an extra space in Dr. Longpre's email that was giving me some trouble when formatting the output.
            email = username + "@utep.edu "
        else:
            email = username + "@utep.edu"
        count = ranking[1]
        row = Professors.loc[Professors["Email"] == email]
        name = str(row.get("Name").values).translate({ord(i): None for i in trashChars}) 
        title = str(row.get("Title").values).translate({ord(i): None for i in trashChars})
        location = str(row.get("Office").values).translate({ord(i): None for i in trashChars})
        phone = str(row.get("Phone").values).translate({ord(i): None for i in trashChars})
        website = str(row.get("Website").values).translate({ord(i): None for i in trashChars})

        print("Rank #", rank, ":", "The serach term","\"",target,"\"", "appears",count, "times")
        print(name +",",title)
        print("Office:",location," Email:",email, " Phone:", phone)
        print("Website:",website)
        print(" ")
        print(" ")
        rank = rank + 1 

# This methof will return on the first word of a string 
def getFirstWord(str):
    return str.split(" ")[0]

# ***** Part 1 *****    

path = os.path.dirname(os.path.realpath(__file__))

sys.setrecursionlimit(10000) # Set the recursion limit to 10,000 so we dont get a depth error when using Pickle 

Professors = constructProfessorsPD() # Create the Professors Panda Dataframe.   Part 1: Task 1 

Professors.to_pickle('professors.pkl') # Store the Professors DF into a Pickle File.    Part 1: Task 2

createWebsiteTextFiles(Professors,path) # Create the txt files of all the Professors' websites.  Part 1: Task 3 & 4 


# ***** Part 2 *****

listOfFiles = createListOfFiles(path)

keepGoing = True
firstTime = True

# loop to keep asking the user for a query term 
while(keepGoing):
    if firstTime:
        unfilteredWord = input("Please Enter a term to Search: ")
        startTime = time.time()
        word = getFirstWord(unfilteredWord)
        print("________________________________________")
        firstTime = False
        wordCount = countWordOccurrences(listOfFiles,word,path)
        createRankingOutput(wordCount,Professors,word)
        print("Time to get ranking:", (time.time() - startTime), "seconds" )
        print("________________________________________")
    else:
        decision = input("Would you like to search or another term? Y or N: ")
        print("________________________________________")
        if decision[0].lower() == "N".lower():
            keepGoing = False
        elif decision[0].lower() == "Y".lower():
            unfilteredWord = input("Please Enter a term to Search: ")
            startTime = time.time()
            word = getFirstWord(unfilteredWord)
            print("________________________________________")
            firstTime = False
            wordCount = countWordOccurrences(listOfFiles,word,path)
            createRankingOutput(wordCount,Professors,word)
            print("Time to get ranking:", (time.time() - startTime), "seconds" )
            print("________________________________________")
        else:
            print("Not a vaild input, exiting program.")
            keepGoing = False


