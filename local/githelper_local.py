#!/usr/bin/python3

import argparse
import subprocess

def list_repos(gitLocation):
    repoStr = subprocess.getoutput("ls" + " " + gitLocation + " " + "| sed -e 's/\.git//g'")
    print(repoStr)

def new_repo(newRepo, gitLocation):
    mkRepoOutput = subprocess.getoutput("git init --bare " + " " + gitLocation + "/" + newRepo + ".git" )
    print(mkRepoOutput)

def clone_repo(cloneRepo, gitLocation):
    cloneOutput = subprocess.getoutput("git clone" + " " + "file:///" + gitLocation + "/" + cloneRepo + ".git") # clones the repo
    print(cloneOutput) # prints output confirming that it was cloned

def archive_repo(archiveRepo, gitLocation):
    print("Archiving " + archiveRepo + " to a tarball")
    cloneOutput = subprocess.getoutput("tar cfvz " + gitLocation + "/" + archiveRepo + ".tgz " + " " + gitLocation + "/" + archiveRepo + ".git/")

def main():
    parser = argparse.ArgumentParser(description='A simple script with multiple command-line flags.')

    # Add the arguments for using your specific server
    parser.add_argument('--loc', default="/srv/git", help='What location should I use?')

    # Add optional flags
    parser.add_argument('--list', '-l', action='store_true', help='Lists existing repos')
    parser.add_argument('--clone', '-c', action='store', help='Clones a repo locally')
    parser.add_argument('--new', '-n', action='store', help='Create a new repo')
    parser.add_argument('--archive', '-a', action='store', help='Compresses a repo into a tarball file')
    
    args = parser.parse_args()
    gitLocation = args.loc

    if args.list:
        list_repos(gitLocation)
    elif args.clone:
        cloneRepo = args.clone
        clone_repo(cloneRepo, gitLocation)
    elif args.new:
        newRepo = args.new
        new_repo(newRepo, gitLocation)
    elif args.archive:
        archiveRepo = args.archive
        archive_repo(archiveRepo, gitLocation)

if __name__ == '__main__':
    main()
