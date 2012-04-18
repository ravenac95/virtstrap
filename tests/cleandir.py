#!/usr/bin/env python
#coding=utf-8
"""
Removes all of the files from the directory not listed in FILELIST.txt

This is for the examples. It will only delete if there is a FILELIST.txt in the
directory that you choose to delete. It was created to ensure portability
between shells
"""
import os
import sys
import shutil

def error_and_exit(msg):
    sys.stderr.write('%s\n' % msg)
    sys.exit(1)

def get_protected_names(file_list_path):
    file_list = open(file_list_path)
    protected_names = ['FILELIST.txt']
    for line in file_list:
        protected_names.append(line.strip())
    return protected_names

def main():
    args = sys.argv[1:]
    if len(args) < 1:
        error_and_exit('A directory is required')
    input_value = args[0]
    directory = os.path.expanduser(input_value)
    directory = os.path.abspath(directory)
    
    if not os.path.isdir(directory):
        error_and_exit('%s (%s) is not a directory' % (input_value, 
            directory))
    file_list_path = os.path.join(directory, 'FILELIST.txt')
    if not os.path.isfile(file_list_path):
        error_and_exit('For safety, the directory to clean'
                ' must have a FILELIST.txt')
    
    dir_list = os.listdir(directory)
    protected_names = get_protected_names(file_list_path)

    for item in dir_list:
        if not item in protected_names:
            # Delete unprotected files/dirs
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

if __name__ == '__main__':
    main()

