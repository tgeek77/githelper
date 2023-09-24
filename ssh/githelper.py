#!/usr/bin/python3

import argparse
import subprocess

def list_repos(sshServer, sshUser):
    repoStr = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "ls")
    print(repoStr)

def clone_repo(cloneRepo, sshServer, sshUser):
    cloneOutput = subprocess.getoutput("git clone" + " " + sshUser + "@" + sshServer + ":~/" + cloneRepo + ".git") # clones the repo
    print(cloneOutput) # prints output confirming that it was cloned

def new_repo(newRepo, sshServer, sshUser):
    mkRepoOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "git init --bare " + newRepo + ".git")
    print(mkRepoOutput)

def archive_repo(archiveRepo, sshServer, sshUser):
    print("Archiving " + archiveRepo + " to a tarball")
    cloneOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "tar cfvz " + archiveRepo + ".tgz " + archiveRepo + ".git/")

def remove_repo(rmRepo, sshServer, sshUser):
    print("Deleting " + rmRepo)
    cloneOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " rm -rfv " + rmRepo + ".git") # deletes the repo
    print(cloneOutput) # prints output confirming that it was deleted

def main():
    parser = argparse.ArgumentParser(description='A simple script with multiple command-line flags.')

    # Add the arguments for using your specific server
    parser.add_argument('--server', help='What server should I use?')
    parser.add_argument('--user', help='What user should I use?')

    # Add optional flags
    parser.add_argument('--list', '-l', action='store_true', help='Lists existing repos')
    parser.add_argument('--clone', '-c', action='store', help='Clones a repo locally')
    parser.add_argument('--new', '-n', action='store', help='Create a new repo')
    parser.add_argument('--archive', '-a', action='store', help='Compresses a repo into a tarball file')
    parser.add_argument('--remove', action='store', help='Deletes a repo')
    
    args = parser.parse_args()
    sshServer = args.server
    sshUser = args.user

    if args.list:
        list_repos(sshServer, sshUser)
    elif args.clone:
        cloneRepo = args.clone
        clone_repo(cloneRepo, sshServer, sshUser)
    elif args.new:
        newRepo = args.new
        new_repo(newRepo, sshServer, sshUser)
    elif args.archive:
        archiveRepo = args.archive
        archive_repo(archiveRepo, sshServer, sshUser)
    elif args.remove:
        rmRepo = args.remove
        remove_repo(rmRepo, sshServer, sshUser)

if __name__ == '__main__':
    main()