import os
import git
import socket

notes_dir = os.path.expanduser('~/org-roam/')
repo = git.Repo(notes_dir)

if repo.is_dirty(untracked_files=True):
    repo.git.add(A=True)
    repo.git.commit('-m', 'Automated commit at midnight', '--author='+socket.gethostname())

