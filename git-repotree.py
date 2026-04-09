import shutil
from git import Repo
import requests
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import print_formatted_text
import os
import stat
from termcolor import colored
from tabulate import tabulate
from pyfiglet import figlet_format
from git.remote import RemoteProgress
import argparse

# Progress Bar for Git Clone
class PrettyProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        stage = op_code & self.OP_MASK

        if stage == self.COUNTING:
            stage_name = "Counting objects"
        elif stage == self.COMPRESSING:
            stage_name = "Compressing"
        elif stage == self.RECEIVING:
            stage_name = "Receiving"
        elif stage == self.RESOLVING:
            stage_name = "Resolving"
        else:
            stage_name = "Cloning"

        if max_count:
            percent = (cur_count / max_count) * 100
            print(f"\r{stage_name}: {percent:.1f}% {message}", end="")

# Clear the terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Handle read-only files on Windows
def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Print Pyfiglet title
def print_title(title):
    title = figlet_format(title, font="slant")
    print_formatted_text(HTML(f'<ansired>{title}</ansired>'))

# Repository name and username from Github URL
def repository_info(github_url):
    repository_user = github_url.split("/")[-2]
    repository_name = github_url.split("/")[-1].replace(".git", "")

    return repository_user, repository_name

# Select branch from available ones
def select_branch(repository_user, repository_name):
    branches_url = f"https://api.github.com/repos/{repository_user}/{repository_name}/branches"

    data = requests.get(branches_url).json()
    branches = [branch["name"] for branch in data]

    # Convert to table format
    columns = 3

    # Split the list into rows
    rows = [branches[i:i+columns] for i in range(0, len(branches), columns)]

    # Pad last row (if more than one row)
    for i, row in enumerate(rows):
        if len(row) < columns and i>0:
            row += [""] * (columns - len(row))

    invalid_branch = True

    while invalid_branch:
        # Print with border
        print_formatted_text(HTML('\n<ansiyellow>Select a branch:</ansiyellow>'))
        print(tabulate(rows, tablefmt="fancy_grid"))

        # Create a completer
        branch_completer = WordCompleter(branches, ignore_case=True)

        # Prompt the user
        selected_branch = prompt('',
            completer=branch_completer
        )

        invalid_branch = selected_branch not in branches
        
        if invalid_branch:
            clear_terminal()
            print_title()
            print_formatted_text(f"\nInvalid branch name (<ansired>{selected_branch}</ansired>)!!!")
        

    return selected_branch

# Git clone of the selected branch for the input Github repository
def git_clone(github_url, selected_branch, folder):
    key = prompt(HTML('\nPress any key to continue by cloning the repository...'))

    if os.path.exists(folder):
        print(f"Removing the existing folder {folder}...", end=' ')
        shutil.rmtree(folder, onexc=remove_readonly)
        print("DONE")

    repo = Repo.clone_from(
        github_url,
        folder,
        branch=selected_branch, 
        single_branch=True,
        progress=PrettyProgress()
    )

    print("\nClone completed !!!")

    all_files = []

    try:
        files = repo.git.ls_files().splitlines()
        all_files.extend(files)
    except:
        pass

    return all_files

# Save all file paths in a TXT file
def save_wordlist(all_files, path_file):
    if os.path.exists(path_file):
        print(f"Removing the existing file {path_file}...", end=' ')
        os.remove(path_file)
        print("DONE")
    
    print(f"Writing the results to {colored(path_file, 'yellow')}...", end=' ')
    
    with open(path_file, "w") as fd:
        for path in sorted(all_files):
            fd.write("/"+path+"\n")

    print("DONE")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Git-RepoTree: Clone a branch and enumerate file paths"
    )

    parser.add_argument(
        "github_url",
        help="GitHub repository URL (e.g. https://github.com/user/repo)"
    )

    return parser.parse_args()

# Main function
def main():
    clear_terminal()
    print_title("Git-RepoTree")

    # Retrieve information about the repository
    args = parse_args()
    github_url = args.github_url
    repository_user, repository_name = repository_info(github_url)
    github_url = f"https://github.com/{repository_user}/{repository_name}.git"

    # List all the branches of the repository and select the desired one
    selected_branch = select_branch(repository_user, repository_name)
    clear_terminal()
    print_title("Git-RepoTree")
    
    # Resume of input values
    print_formatted_text(HTML(f'Github URL: <ansiyellow>{github_url}</ansiyellow>'))
    print_formatted_text(HTML(f'Username:   <ansiyellow>{repository_user}</ansiyellow>'))
    print_formatted_text(HTML(f'Repository: <ansiyellow>{repository_name}</ansiyellow>'))
    print_formatted_text(HTML(f'Branch:     <ansigreen>{selected_branch}</ansigreen>'))

    # Clone the branch of the Github repository
    folder = f"{repository_name}-{selected_branch}"
    all_files = git_clone(github_url, selected_branch, folder)

    # Save all the file paths in a TXT file
    path_file = f"{repository_name}-{selected_branch}.txt"
    save_wordlist(all_files, path_file)

if __name__=="__main__":
    main()