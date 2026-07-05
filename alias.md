# Example shell aliases for githelper subcommands.
# Adjust paths, server, user, dir, and port for your setup.

GH="python3 /path/to/githelper/cli/githelper.py"
REMOTE="$GH --server example.com --user git --dir git --port 2222"

# Remote bare-repo shortcuts
alias ghlist='$REMOTE remote list'
alias ghclone='$REMOTE remote clone'
alias ghnew='$REMOTE remote create'
alias ghdelete='$REMOTE remote delete'
alias gharch='$REMOTE remote archive'
alias ghfork='$REMOTE remote fork'
alias ghrename='$REMOTE remote rename'
alias ghinfo='$REMOTE remote info'

# Local bare-repo shortcuts
alias lghlist='$GH --loc /mnt/disk bare list'
alias lghclone='$GH --loc /mnt/disk bare clone'
alias lghnew='$GH --loc /mnt/disk bare create'
alias lgharch='$GH --loc /mnt/disk bare archive'

# Heatmap (uses local_repo_base from ~/.githelperrc when --base omitted)
alias ghmap='$GH heatmap'
