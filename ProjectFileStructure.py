import os
import argparse

parser = argparse.ArgumentParser("python ProjectFileStructure.py", description='Tool for visualizing the project directory structure.')
parser.add_argument("-f", "--includefilenames", default=False, help="List the files in the project as well as the directory structure", action="store_true")
args = parser.parse_args()

show_filenames = args.includefilenames

def list_files(startpath):
    excluded = set(['bin', 'obj', 'node_modules', 'dist', 'packages', '.git', '.vs'])
    for root, dirs, files in os.walk(startpath, topdown=True):
        found = False
        for folder in excluded:
            if folder in root:
                found = True
        if not found:
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            if show_filenames:
                subindent = ' ' * 4 * (level + 1)
                for f in files:
                    print('{}{}'.format(subindent, f))

list_files('.')
