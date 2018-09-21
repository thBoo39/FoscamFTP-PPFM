'''
DirStateCmp module is used to scan files. It can read the file structure, save to json file, and load from json file.

DirStateCmp.state has the following dictionary structure.
    name: file or folder name
    type: file or folder
    children:
        name: file or folder name
        type: file or folder
        time: timestamp (since modified)

Thanks to the idea by ThomasSileo, "Tracking Changes in Directories with Python"
'''
import os
from sys import platform
import json
import pprint
import errno
from collections import defaultdict


class DirState(object):
    '''
    Read file names and timestamps in the specified directory.
    Return a nested dictionary structure upon instantiation.
    Use method to_json(path) to save the structure to json file.
    Use method from_json(path) to load the structure file from the json file.
    '''
    def __init__(self, path="", state=None):
        self.path = path
        # need error check like if path is exist
        self.state = state or self.get_state(path)
        return

    def to_json(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self.state))

        return

    @classmethod
    def from_json(cls, state_file):
        with open(state_file, 'r') as f:
            return cls(state = json.load(f))

    @staticmethod
    def get_state(path):
        '''
        path is a folder. Expect the following structure:
        name: path
        type: folder
        children:
            name: path
            type: file
            time: timestamp
        '''
        if len(path) > 0:
            state = DirState.path_to_dict(path)
            state = DirState.add_timestamp(state, path)
        else:
            state = {'name': "", 'type': "folder", 'time': 0, 'children': [{'name': "", 'type': "", 'time': 0}]}
        return state

    @staticmethod
    def path_to_dict(path):
        d = {'name': os.path.basename(path)}
        if os.path.isdir(path):
            d['type'] = "folder"
            d['children'] = [DirState.path_to_dict(os.path.join(path, x)) for x in os.listdir(path)]
        else:
            d['type'] = "file"
        return d

    @staticmethod
    def add_timestamp(data, path=""):
        if path == "":
            path = data['name']
        # print "path:", path
        for child in data['children']:
            if child['type'] == 'folder':
                # print 'Folder name:', child['name']
                DirState.add_timestamp(child, os.path.join(path, child['name']))
            else:
                # print "Filename:", child['name']
                child['time'] = os.path.getmtime(os.path.join(path, child['name']))
        return data


def to_list(data, list_data, path = ""):
    '''
    Return list of files and index (timestamp)
    '''
    list_file = list_data[0]
    list_index = list_data[1]
    if path == "":
        path = data['name']
    for child in data['children']:
        if child['type'] == 'folder':
            to_list(child, (list_file, list_index), os.path.join(path, child['name']))
        else:
            if len(child['name']) > 0:
                add_this = os.path.join(path, child['name'])
            else:
                print("addthis")
                add_this = ""
            list_file.append(add_this)
            list_index.append(child['time'])
    return list_file, list_index



def to_dict(data):
    '''
    data: nexted dictionary type
    return dictionary type with files('files') and their timestamps('index')
    '''
    list_file = []
    list_index = []
    list_file, list_index = to_list(data, [list_file, list_index])
    return dict(files=list_file, index=list_index)


def compute_dir_index(path):
    files = []
    subdirs = []
    index = {}
    for root, dirs, filenames in os.walk(path):
        for subdir in dirs:
            subdirs.append(os.path.relpath(os.path.join(root, subdir), path))
        for fname in filenames:
            files.append(os.path.relpath(os.path.join(root, fname), path))
    for fname in files:
        index[fname] = os.path.getmtime(os.path.join(path, fname))
    # print subdirs
    # print files
    # print index
    return dict(files = files, subdirs = subdirs, index = index)


def compute_diff(old_set, new_set):
    data = {}
    data['deleted'] = list(set(old_set['files']) - set(new_set['files']))
    data['created'] = list(set(new_set['files']) - set(old_set['files']))
    data['updated'] = []
    # data['deleted_dirs'] = list(set(dir_cmp['subdirs']) - set(dir_base['subdirs']))

    for i, fname in enumerate(old_set['files']):
        if fname in new_set['files']:
            if old_set['index'][i] < new_set['index'][i]:
                data['updated'].append(new_set['files'][i])

    return data


def main():
    return


if __name__ == "__main__":
    main()
