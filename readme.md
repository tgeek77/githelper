# githelper
Tools to make your own private git repos without needing any extra frameworks.

## About:

A lot of use want to create our own private git repos without needing to rely on third-party tools like Github, Gitlab, or even Gitea. If you're concerned about privacy, cloud-based tools always present issues because Terms of Service could change at any time, not to mention the fact that well known services tend to be target for hackers. Even self-hosting a service like Gitea or Gitlab means that you need to worry about the proper care and updates of this software. Often, they have have tons of services that you will never needs.

Instead, what about just using git directly to create and clone repos without needing all of the overhead of these other systems? My scripts do that. They give you a way to quickly create a new repo on a remote machine or even on your local machine, clone the repo that you just created, and start working. These scripts are simple and they each only do one job.

I hope they make your work a little easier if you want to go away from big hosted services.

## Update:

aliases.md contains a few BASH aliases that you can use with githelper.

I thought long a hard about writing a function into githelper that would cache your settings so you don't have to write them manually every time. I think wrapping a simple alias around the command is a better way to go.

There is one more option if you don't want to use aliases:

Open githelper.py in a text editor and look for this code:

```
# Add the arguments for using your specific server
parser.add_argument('--server', default="example.com", help='What server should I use?')
parser.add_argument('--user', default="tux", help='What user should I use?')
```

You can simple change `example.com` to your server and you change `tux` to your server and username. 

You can do the same thing with the port number. Personally, I don't use the standard port 22. If you're like me, you can change that also.
```
parser.add_argument('--port', '-p', default="22", help='Set the ssh port to something other than 22')
```

