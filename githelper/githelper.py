#!/usr/bin/python3
"""
Create and admin Git repos locally or remotely without external tools
"""

import argparse
import subprocess
import sys

def list_repos(location, ssh_server=None, ssh_user=None, ssh_port=None, remote=False):
    """
    Lists repos locally or via SSH
    """
    if remote:
        repo_list = f"ssh {ssh_user}@{ssh_server} -p {ssh_port} \
        ls {location}/ | sed -e 's/\\.git//g'"
    else:
        repo_list = f"ls {location} | sed -e 's/\\.git//g'"
    
    list_result = subprocess.run(repo_list, shell=True, check=True, capture_output=True, text=True)
    print(list_result.stdout.strip())
    return list_result.stdout

def rename_repo(location, new_repo, old_repo, ssh_server=None, ssh_user=None, ssh_port=None, remote=False):
    """
    Renames repos locally or via SSH
    """
    if remote:
        rename_cmd = f"ssh {ssh_user}@{ssh_server} -p {ssh_port} \
        mv -v {location}/{old_repo}.git {location}/{new_repo}.git"
    else:
        rename_cmd = f"mv -v {location}/{old_repo}.git {location}/{new_repo}.git"
    
    rename_result = subprocess.run(rename_cmd, shell=True, check=True, capture_output=True, text=True)
    print(rename_result.stdout.strip())
    return rename_result.stdout

def fork_repo(location, new_repo, old_repo, ssh_server=None, ssh_user=None, ssh_port=None, remote=False):
    """
    Copies (forks) repos locally or via SSH
    """
    if remote:
        fork_cmd = f"ssh {ssh_user}@{ssh_server} -p {ssh_port} \
        cp -rv {location}/{old_repo}.git {location}/{new_repo}.git"
    else:
        fork_cmd = f"cp -rv {location}/{old_repo}.git {location}/{new_repo}.git"
    
    fork_result = subprocess.run(fork_cmd, shell=True, check=True, capture_output=True, text=True)
    print(fork_result.stdout.strip())
    return fork_result.stdout

def clone_repo(clone_repo, location, ssh_server=None, ssh_user=None, ssh_port=None, remote=False):
    """
    Clones repo locally or from remote server
    """
    if remote:
        clone_cmd = f"git clone ssh://{ssh_user}@{ssh_server}:{ssh_port}/~/{location}/{clone_repo}.git"
    else:
        clone_cmd = f"git clone file:///{location}/{clone_repo}.git"
    
    clone_result = subprocess.run(clone_cmd, shell=True, check=True, capture_output=True, text=True)
    print(clone_result.stdout.strip())
    return clone_result.stdout

def create_repo(new_repo, location, ssh_server=None, ssh_user=None, ssh_port=None, remote=False):
    """
    Creates repos locally or via SSH
    """
    if remote:
        create_cmd = f"ssh {ssh_user}@{ssh_server} -p {ssh_port} \
        git init --bare {location}/{new_repo}.git"
    else:
        create_cmd = f"git init --bare {location}/{new_repo}.git"
    
    create_result = subprocess.run(create_cmd, shell=True, check=True, capture_output=True, text=True)
    print(create_result.stdout.strip())
    return create_result.stdout

def archive_repo(archive_repo, location, ssh_server=None, ssh_user=None, ssh_port=None, remote=False):
    """
    Archives a repo locally or via SSH
    """
    print(f"Archiving {archive_repo} to a tarball")
    if remote:
        archive_cmd = f"ssh {ssh_user}@{ssh_server} -p {ssh_port} \
        tar cfvz {archive_repo}.tgz {location}/{archive_repo}.git/"
    else:
        archive_cmd = f"tar cfvz {location}/{archive_repo}.tgz {location}/{archive_repo}.git/"
    
    archive_result = subprocess.run(archive_cmd, shell=True, check=True, capture_output=True, text=True)
    print(archive_result.stdout.strip())
    return archive_result.stdout

def remove_repo(rm_repo, location, ssh_server=None, ssh_user=None, ssh_port=None, remote=False):
    """
    Deletes a repo locally or via SSH
    """
    print(f"Deleting {rm_repo}")
    if remote:
        del_cmd = f"ssh {ssh_user}@{ssh_server} -p {ssh_port} \
        rm -rfv {location}/{rm_repo}.git"
    else:
        del_cmd = f"rm -rfv {location}/{rm_repo}.git"
    
    del_result = subprocess.run(del_cmd, shell=True, check=True, capture_output=True, text=True)
    print(del_result.stdout.strip())
    return del_result.stdout

def main():
    """
    Gathers user input and determines local vs remote operation
    """
    parser = argparse.ArgumentParser(
        description='Manage Git repositories locally or remotely via SSH')

    # Location arguments
    parser.add_argument('--loc', '--dir', '-d',
        default="/srv/git",
        help='Directory where git repos are located (default: /srv/git)')
    
    # Remote server arguments
    parser.add_argument('--server',
        help='SSH server hostname (enables remote mode)')
    parser.add_argument('--user',
        default="git",
        help='SSH username (default: git)')
    parser.add_argument('--port', '-p',
        default="22",
        help='SSH port (default: 22)')

    # Operation flags
    parser.add_argument('--list', '-l',
        action='store_true',
        help='List existing repos')
    parser.add_argument('--clone', '-c',
        action='store',
        help='Clone a repo locally')
    parser.add_argument('--new', '-n',
        action='store',
        help='Create a new repo')
    parser.add_argument('--archive', '-a',
        action='store',
        help='Compress a repo into a tarball file')
    parser.add_argument('--remove', '--rm',
        action='store',
        help='Delete a repo')
    parser.add_argument('--rename', '-rn',
        action='store_true',
        help='Rename repo (requires --old-repo and --new-repo)')
    parser.add_argument('--fork', '-f',
        action='store_true',
        help='Copy/fork repo (requires --old-repo and --new-repo)')
    
    # Rename/fork specific arguments
    parser.add_argument('--old-repo',
        help='Old repo name (used with --rename or --fork)')
    parser.add_argument('--new-repo',
        help='New repo name (used with --rename or --fork)')

    args = parser.parse_args()
    
    # Determine if we're operating remotely
    remote = bool(args.server)
    location = args.loc
    
    # Validate remote-specific arguments
    if remote and not all([args.server, args.user]):
        print("Error: Remote mode requires --server and --user arguments")
        sys.exit(1)
    
    # Validate rename/fork arguments
    if (args.rename or args.fork) and not all([args.old_repo, args.new_repo]):
        print("Error: --rename and --fork require both --old-repo and --new-repo")
        sys.exit(1)

    try:
        if args.list:
            list_repos(location, args.server, args.user, args.port, remote)
        elif args.clone:
            clone_repo(args.clone, location, args.server, args.user, args.port, remote)
        elif args.new:
            create_repo(args.new, location, args.server, args.user, args.port, remote)
        elif args.archive:
            archive_repo(args.archive, location, args.server, args.user, args.port, remote)
        elif args.remove:
            remove_repo(args.remove, location, args.server, args.user, args.port, remote)
        elif args.rename:
            rename_repo(location, args.new_repo, args.old_repo, args.server, args.user, args.port, remote)
        elif args.fork:
            fork_repo(location, args.new_repo, args.old_repo, args.server, args.user, args.port, remote)
        else:
            parser.print_help()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()