#!/usr/bin/python3

import argparse
import subprocess

def list_repos(ssh_server, ssh_user, ssh_port):
    repo_str = subprocess.getoutput("ssh " + ssh_user + "@" + ssh_server + " " + "-p" + ssh_port + " " + "ls" + " " + "| sed -e 's/git//g'")
    print(repo_str)

def clone_Repo(clone_Repo, ssh_server, ssh_user, ssh_port):
    clone_output = subprocess.getoutput("git" + " " + "clone" + " " + "ssh://" + ssh_user + "@" + ssh_server + ":" + ssh_port +  "/~/" + clone_Repo + ".git") # clones the repo
    print(clone_output) # prints output confirming that it was cloned

def new_repo(new_repo, ssh_server, ssh_user, ssh_port):
    mk_repo_output = subprocess.getoutput("ssh " + ssh_user + "@" + ssh_server + " " + "-p" + ssh_port + " " + "git init --bare " + new_repo + ".git")
    print(mk_repo_output)

def archive_repo(archive_repo, ssh_server, ssh_user, ssh_port):
    print("Archiving " + archive_repo + " to a tarball")
    clone_output = subprocess.getoutput("ssh " + ssh_user + "@" + ssh_server  + " " + "-p" + ssh_port + " " + "tar cfvz " + archive_repo + ".tgz " + archive_repo + ".git/")

def remove_repo(rm_repo, ssh_server, ssh_user, ssh_port):
    print("Deleting " + rm_repo)
    clone_output = subprocess.getoutput("ssh " + ssh_user + "@" + ssh_server + " " + "-p" + ssh_port + " " + " rm -rfv " + rm_repo + ".git") # deletes the repo
    print(clone_output) # prints output confirming that it was deleted

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
    ssh_server = args.server
    ssh_user = args.user
    ssh_port = args.port

    if args.list:
        list_repos(ssh_server, ssh_user, ssh_port)
    elif args.clone:
        clone_Repo = args.clone
        clone_Repo(clone_Repo, ssh_server, ssh_user, ssh_port)
    elif args.new:
        new_repo = args.new
        new_repo(new_repo, ssh_server, ssh_user, ssh_port)
    elif args.archive:
        archive_repo = args.archive
        archive_repo(archive_repo, ssh_server, ssh_user, ssh_port)
    elif args.remove:
        rm_repo = args.remove
        remove_repo(rm_repo, ssh_server, ssh_user, ssh_port)

if __name__ == '__main__':
    main()
