#!/usr/bin/python3

import subprocess

mkRepo = input("Repo Name \n")

mkRepoOutput = subprocess.getoutput("ssh git@example.com git init --bare " + mkRepo + ".git")
print(mkRepoOutput)
