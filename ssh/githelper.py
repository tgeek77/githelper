#!/usr/bin/python3

import argparse
import subprocess

def list_repos(sshServer, sshUser, sshPort):
    repoStr = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + "ls" + " " + "| sed -e 's/\.git//g'")
    print(repoStr)

def clone_repo(cloneRepo, sshServer, sshUser, sshPort):
    cloneOutput = subprocess.getoutput("git" + " " + "clone" + " " + "ssh://" + sshUser + "@" + sshServer + ":" + sshPort +  "/~/" + cloneRepo + ".git") # clones the repo
    print(cloneOutput) # prints output confirming that it was cloned

def new_repo(newRepo, sshServer, sshUser, sshPort):
    mkRepoOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + "git init --bare " + newRepo + ".git")
    print(mkRepoOutput)

def archive_repo(archiveRepo, sshServer, sshUser, sshPort):
    print("Archiving " + archiveRepo + " to a tarball")
    cloneOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer  + " " + "-p" + sshPort + " " + "tar cfvz " + archiveRepo + ".tgz " + archiveRepo + ".git/")

def remove_repo(rmRepo, sshServer, sshUser, sshPort):
    print("Deleting " + rmRepo)
    cloneOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + " rm -rfv " + rmRepo + ".git") # deletes the repo
    print(cloneOutput) # prints output confirming that it was deleted

def main():
    parser = argparse.ArgumentParser(description='A simple script with multiple command-line flags.')

    # Add the arguments for using your specific server
    parser.add_argument('--server', default="example.com", help='What server should I use?')
    parser.add_argument('--user', default="tux", help='What user should I use?')

    # Add optional flags
    parser.add_argument('--list', '-l', action='store_true', help='Lists existing repos')
    parser.add_argument('--clone', '-c', action='store', help='Clones a repo locally')
    parser.add_argument('--new', '-n', action='store', help='Create a new repo')
    parser.add_argument('--archive', '-a', action='store', help='Compresses a repo into a tarball file')
    parser.add_argument('--remove', action='store', help='Deletes a repo')
    parser.add_argument('--port', '-p', default="22", help='Set the ssh port to something other than 22')

    args = parser.parse_args()
    sshServer = args.server
    sshUser = args.user
    sshPort = args.port

    if args.list:
        list_repos(sshServer, sshUser, sshPort)
    elif args.clone:
        cloneRepo = args.clone
        clone_repo(cloneRepo, sshServer, sshUser, sshPort)
    elif args.new:
        newRepo = args.new
        new_repo(newRepo, sshServer, sshUser, sshPort)
    elif args.archive:
        archiveRepo = args.archive
        archive_repo(archiveRepo, sshServer, sshUser, sshPort)
    elif args.remove:
        rmRepo = args.remove
        remove_repo(rmRepo, sshServer, sshUser, sshPort)

if __name__ == '__main__':
    main()
