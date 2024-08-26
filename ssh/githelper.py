#!/usr/bin/python3

import argparse
import subprocess

def list_repos(sshServer, sshDir, sshUser, sshPort):
    repoStr = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + "ls" + " " + sshDir + "/" + " " + "| sed -e 's/\\.git//g'")
    print(repoStr)

def rename_repo(sshServer, sshDir, sshUser, sshPort, newRepo, oldRepo):
    renameRepo = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + "mv -v " + sshDir + '/' + oldRepo + ".git " + sshDir + '/' + newRepo + ".git")
    print(renameRepo)

def fork_repo(sshServer, sshDir, sshUser, sshPort, newRepo, oldRepo):
    forkRepo = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + "cp -rv " + sshDir + '/' + oldRepo + ".git " + sshDir + '/' + newRepo + ".git")
    print(forkRepo)

def clone_repo(cloneRepo, sshServer, sshDir, sshUser, sshPort):
    cloneOutput = subprocess.getoutput("git" + " " + "clone" + " " + "ssh://" + sshUser + "@" + sshServer + ":" + sshPort + " " + sshDir + '/' + cloneRepo + ".git") # clones the repo
    print(cloneOutput) # prints output confirming that it was cloned

def new_repo(newRepo, sshServer, sshDir, sshUser, sshPort):
    mkRepoOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + "git init --bare " + sshDir + '/' + newRepo + ".git")
    print(mkRepoOutput)

def archive_repo(archiveRepo, sshServer, sshDir, sshUser, sshPort):
    print("Archiving " + archiveRepo + " to a tarball")
    cloneOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer  + " " + "-p" + sshPort + " " + "tar cfvz " + archiveRepo + ".tgz " + sshDir + '/' + archiveRepo + ".git/")

def remove_repo(rmRepo, sshServer, sshDir, sshUser, sshPort):
    print("Deleting " + rmRepo)
    cloneOutput = subprocess.getoutput("ssh " + sshUser + "@" + sshServer + " " + "-p" + sshPort + " " + " rm -rfv " + sshDir + '/' + rmRepo + ".git") # deletes the repo
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
    parser.add_argument('--rename', '-rn', action='store_true', help='Rename repo')
    parser.add_argument('--fork', '-f', action='store_true', help='Copy repo')
    parser.add_argument('--oldrepo', action='store', help='Old Name (Used with fork or rename)')
    parser.add_argument('--newrepo', action='store', help='New Name (Used with fork or rename)')
    parser.add_argument('--dir', '-d', default=".", action='store', help='Set the directory where your git repos are located on the server')

    args = parser.parse_args()
    sshServer = args.server
    sshUser = args.user
    sshPort = args.port
    sshDir = args.dir
    newRepo = args.newrepo
    oldRepo = args.oldrepo
    rename = args.rename
    fork = args.fork

    if args.list:
        list_repos(sshServer, sshDir, sshUser, sshPort)
    elif args.clone:
        cloneRepo = args.clone
        clone_repo(cloneRepo, sshServer, sshDir, sshUser, sshPort)
    elif args.new:
        newRepo = args.new
        new_repo(newRepo, sshServer, sshDir, sshUser, sshPort)
    elif args.archive:
        archiveRepo = args.archive
        archive_repo(archiveRepo, sshServer, sshDir, sshUser, sshPort)
    elif args.remove:
        rmRepo = args.remove
        remove_repo(rmRepo, sshServer, sshDir, sshUser, sshPort)
    elif args.rename:
        rename_repo(sshServer, sshDir, sshUser, sshPort, newRepo, oldRepo)
    elif args.fork:
        fork_repo(sshServer, sshDir, sshUser, sshPort, newRepo, oldRepo)

if __name__ == '__main__':
    main()