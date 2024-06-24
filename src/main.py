import os
from git import Repo

current_dir = os.path.dirname(os.path.abspath(__file__))

repo_url = 'https://github.com/processing/p5.js'
repo_name = repo_url.split('/')[-1].replace('.git', '')
local_dir = os.path.join(current_dir,'tmp',repo_name)

Repo.clone_from(repo_url, local_dir)
