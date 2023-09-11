#!/usr/bin/python3
import subprocess

repoList = ()

# Intro
print("This script assumes that /srv/git has been created and you have access to it. \n")

# get list of repos and put them into a collection
repoStr = subprocess.getoutput("ls /srv/git/")

# Convert the string to a list
def Convert(string):
    li = list(string.split("\n"))
    return li
  
# create the list
repoList = ((Convert(repoStr)))

# Print the list
for (i, item) in enumerate(repoList, start=0):
    print(i, item)

# ask for the repo number
cloneReq = input("Which Repo? \n")
cloneReq = int(cloneReq)
cloneRepo = (repoList[cloneReq])
cloneOutput = subprocess.getoutput("git clone file:///srv/git/" + cloneRepo) # clones the repo
print(cloneOutput) # prints output confirming that it was cloned
