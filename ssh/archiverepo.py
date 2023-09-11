#!/usr/bin/python3

import subprocess

repoList = ()

# get list of repos and put them into a collection
repoStr = subprocess.getoutput("ssh git@example.com 'ls'")

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
print("Archiving Repo to a tarball")
cloneOutput = subprocess.getoutput("ssh git@example.com tar cfvz " + cloneRepo + ".tgz " + cloneRepo + "/")
print("Deleting Repo but not the archive!")
cloneOutput = subprocess.getoutput("ssh git@example.com rm -rf " + cloneRepo) # clones the repo
print(cloneOutput) # prints output confirming that it was cloned
