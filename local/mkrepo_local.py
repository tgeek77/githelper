#!/usr/bin/python3

# Intro
print("This script assumes that /srv/git has been created and you have access to it. \n")

import subprocess

mkRepo = input("Repo Name \n")

mkRepoOutput = subprocess.getoutput("cd /srv/git && git init --bare " + mkRepo + ".git")
print(mkRepoOutput)
