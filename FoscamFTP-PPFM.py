#!/usr/bin/python
'''
File names produced by FTP feature of Foscam camera FI9800p is in the format 'MDAlarm_yyyymmdd-hhmmss.jpg' and sent into a single folder. If there are hundreds of image files not sorted, it becomes chaotic. Often, it is convenient if files are placed in folders in date format.
This python code solves the problem. It scans the FTP created folder, sorts the image files into folders by date. It can also delete old images past a specified days.

If folder contains sub folders, it yields an error.
'''
from __future__ import print_function
import json
import datetime
import os
import shutil
import argparse
# Custom modules
import DirStateCmp


def create_folder(path):
    if not os.path.exists(path):
        print("Creating a folder:", path)
        os.makedirs(path)
    return


def copy_file(src_fname, dst_fname):
    shutil.copyfile(src_fname, dst_fname)
    print("Copy from", src_fname, "To", dst_fname)
    return


def sort_by_date(state, s):
    '''
    Copy files (state) into folder (save_path) by date.
    Create folders if not exist.
    Delete files in the original folder unless 'keep-files' is specified.
    '''
    date_list = []
    for item in state['children']:
        fname = item['name']
        dt = datetime.datetime.strptime(fname, s['fformat'])
        folder_name = dt.strftime(s['wfformat'])
        dst_folder = os.path.join(s['save_path'], folder_name)
        if folder_name not in date_list:
            date_list.append(folder_name)
            create_folder(dst_folder)
        dst_fname = dt.strftime(s['wfnformat'])
        dst_fpath = os.path.join(dst_folder, dst_fname)
        src_fpath = os.path.join(s['load_path'], fname)
        copy_file(src_fpath, dst_fpath)
        if s['keep_files'] is not True:
            os.remove(src_fpath)
    return


def delete_old_files(state, s):
    '''
    File structure should be:
    save_path:
        date1:
            files
        date2:
            files
    if time delta, current time - folder name date is less than day2save,
    do nothing, otherwise scan files and determine if deletion is necessary.
    '''
    tm_now = datetime.datetime.now()
    # Scan folders in save_path
    for item in state['children']:
        folder_name = item['name']
        dt = datetime.datetime.strptime(folder_name, s['wfformat'])
        delta_days = tm_now-dt
        if delta_days.days < s['day2save']:
            pass
        # If the folder is empty, delete the folder
        elif len(item['children']) == 0:
            folder_path = os.path.join(s['save_path'], folder_name)
            print("Delete the empty folder:", folder_path)
            os.rmdir(folder_path)
        else:
            # Scan files in the folder corresponding to more than day2save-1
            # Some files are not reaching day2save days yet
            folder_path = os.path.join(s['save_path'], folder_name)
            num_file_left = len(item['children'])
            for files in item['children']:
                fname = files['name']
                tm = datetime.datetime.strptime(fname, s['wfnformat'])
                tm_file = datetime.datetime.strptime(dt.strftime("%Y%m%d")+ tm.strftime("%H%M%S"), "%Y%m%d%H%M%S")
                delta = tm_now-tm_file
                if delta.days >= s['day2save']:
                    path_delete = os.path.join(folder_path, fname)
                    print("Deleting:", path_delete)
                    os.remove(path_delete)
                    num_file_left -= 1
            # This is to ensure deleting a folder if the folder becomes empty
            if num_file_left == 0:
                print("Deleting the empty folder:", folder_path)
                os.rmdir(folder_path)
    return

def main():
    parser = argparse.ArgumentParser(description='Foscam FTP post process file manager (PPFM)')
    parser.add_argument('-s','--src', help='Source Foscam FTP folder', required=True)
    parser.add_argument('-d','--dst', help='Destination folder', required=True)
    parser.add_argument('--day', help='Days to keep image files (default: 7 days)', default=7)
    parser.add_argument('--foscam-format', help='Foscam FTP file name format (default: MDAlarm_%%Y%%m%%d-%%H%%M%%S.jpg)', default='MDAlarm_%Y%m%d-%H%M%S.jpg')
    parser.add_argument('--folder-format', help='folder name format (default: %%Y%%m%%d)', default="%Y%m%d")
    parser.add_argument('--file-format', help='file name format (default: %%H%%M%%S.jpg)', default='%H%M%S.jpg')
    parser.add_argument('--keep-files', help='keep the original image files if specified', action='store_true')
    args = parser.parse_args()
    if not os.path.exists(args.src):
        print("Source folder does not exist.")
        return
    if not os.path.exists(args.dst):
        create_folder(args.dst)
    settings = {
        'load_path':args.src,  # path to the Foscam FTP folder
        'save_path':args.dst,  # path to the folder to save
        'day2save':args.day,  # period to keep folders. If longer, delete it.
        'fformat':args.foscam_format,  # Foscam FTP file name format
        'wfformat':args.folder_format,  # write folder format
        'wfnformat':args.file_format,  # write file name format
        'keep_files':args.keep_files  # keep the original files
        }
    # print info
    print("Working folder:", settings['load_path'])
    print("Saving path:", settings['save_path'])
    # Get the files from Foscam FTP folder
    dir_state = DirStateCmp.DirState(settings['load_path'])
    # Sort files into folders
    sort_by_date(dir_state.state, settings)
    # Get file structure in saved folders
    dir_state = DirStateCmp.DirState(settings['save_path'])
    # Delete old files exceeding days specified by day2save
    delete_old_files(dir_state.state, settings)
    return


if __name__ == "__main__":
    main()
