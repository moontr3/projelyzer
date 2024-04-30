from typing import *
import glob
import os
from .config import *


class File:
    def __init__(self, path:str, encoding:str=DEFAULT_ENCODING):
        '''
        Represents a file.

        `File.check()` rechecks the current file.

        > Note that this will NOT modify the parent
        `Project` info even if the file data has changed.

        `File.path` - passed path
        `File.abs_path` - absolute path
        `File.rel_path` - relative path
        `File.filename` - full filename with extension
        `File.name` - file name without extension
        `File.extension` - file extension
        '''
        self.encoding: str = encoding

        self.path: str = path
        self.abs_path: str = os.path.abspath(path)
        self.rel_path: str = os.path.relpath(path)
        self.filename: str = os.path.basename(path)
        self.name, self.extension = os.path.splitext(path)

        self.check()


    def check(self):
        '''
        Rechecks the file.

        Uses `File.encoding` to read the files with
        a specific encoding. `utf-8` by default.
        '''
        self.size: int = os.path.getsize(self.path)

        # reading the file
        with open(self.path, encoding=self.encoding) as f:
            self.contents: str = f.read()

        self.lines: int = self.contents.count('\n') # total lines of code in file
        self.characters: int = len(self.contents) # total chars in file


class Project:
    def __init__(
        self, parent:str,
        max_file_size:int=MAX_SIZE,
        exclude_extensions:List[str]=DEFAULT_EXCLUDED_EXTENSIONS,
        exclude_dirs:List[str]=DEFAULT_EXCLUDED_DIRECTORIES
    ):
        '''
        Represents a project.

        `Project.check()` recursively rechecks the current directory.

        `Project.parent` - passed path
        `Project.abs_path` - absolute parent path
        `Project.rel_path` - relative path
        `Project.max_file_size` - maximum allowed filesize
        `Project.exclude_ext` - list of extensions to exclude
        `Project.exclude_dir` - list of folder names to exclude files within
        '''
        self.parent: str = parent
        self.abs_path: str = os.path.abspath(parent)
        self.rel_path: str = os.path.relpath(parent)

        self.max_file_size: int = max_file_size
        self.exclude_ext: List[str] = exclude_extensions
        self.exclude_dir: List[str] = exclude_dirs

        self.check()


    def check(self, no_warns:bool=True):
        '''
        Rechecks the project.

        `no_warns` prevents all WARN log entries from outputting.
        '''
        # preparing
        self.files: List[File] = [] # list of files
        self.lines: int = 0 # total lines of code
        self.characters: int = 0 # total characters in files
        self.unexcluded_weight: int = 0 # total weight of unexcluded files
        self.total_weight: int = 0 # total project weight
        self.unexcluded_ext_leaders: Dict[str, int] = {}
        self.total_ext_leaders: Dict[str, int] = {}
 
        # searching for files
        for file in glob.glob(self.abs_path+'/**', recursive=True):
            if os.path.isfile(file):
                # recording global info
                size: int = os.path.getsize(file)
                self.total_weight += size

                _, ext = os.path.splitext(file)
                if ext not in self.total_ext_leaders:
                    self.total_ext_leaders[ext] = 0
                self.total_ext_leaders[ext] += 1

                # file too big
                if size > self.max_file_size: 
                    continue
                
                # file extension excluded
                if ext in self.exclude_dir:
                    continue

                # filepath excluded
                path = os.path.dirname(file)
                if True in [i in self.exclude_dir for i in path]:
                    continue

                # reading file
                try:
                    file_obj = File(file)
                except Exception as e:
                    if not no_warns:
                        print(f'WARN: Exception occured while loading {file}: {e}')
                    continue

                print(f'INFO: Loaded file {file}')

                # recording info
                self.files.append(file_obj)

                self.lines += file_obj.lines
                self.characters += file_obj.characters
                self.unexcluded_weight += size

                if ext not in self.unexcluded_ext_leaders:
                    self.unexcluded_ext_leaders[ext] = 0
                self.unexcluded_ext_leaders[ext] += 1

        # sorting leaders
        self.unexcluded_ext_leaders =\
            dict(sorted(self.unexcluded_ext_leaders.items(), key=lambda x: x[1]))
        self.total_ext_leaders =\
            dict(sorted(self.total_ext_leaders.items(), key=lambda x: x[1]))
