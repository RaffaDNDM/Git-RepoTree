# Git-RepoTree
**Git-RepoTree** is a tool that allows you to:
* Select a branch from a GitHub repository
* Clone only that branch locally
* Extract and save all file paths
* Use the output for content discovery, fuzzing, or security analysis

## Installation
Clone the repository:

```bash
git clone https://github.com/yourusername/git-repotree.git
cd git-repotree
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python git-repotree.py https://github.com/user/repository
```
or
```bash
python git-repotree.py https://github.com/user/repository.git
```

## Output (`<repository>-<branch>.txt`)
```
/index.php
/config.php
/admin/index.php
/...
```