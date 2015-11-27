import sys
import time
import os
import shutil

import organize.organizerErros as OrganizerExceptions
from organize.balance import Balancer
from organize.balanceConstants import BalanceConstants
from organize.unknownFiles import UnknownFiles
from organize.fileRemover import FileRemover
from organize.filesToTop import FilesToTop
from organize.organizer import Organizer
from organize.names import Names
from organize.nameAdder import NameAdder
from organize.createTestFiles import CreateTestFiles
from organize.directoryMover import DirectoryMover
from organize.addDirNameToFiles import AddDirNameToFiles
from organize.unknownFilesInterface import UnknownFilesController

class RunOrganizer(object):
    def __init__(self, args):
        self.args = args
        self.valid_args = [
            'balance',
            'movedirs',
            'adddir',
            'unknown',
            'unknowncontroller'
            'remove',
            'organize',
            'addnames',
            'testfiles',
            'cachenames'
        ]

    def run(self):
        try:
            del self.args[0]
            control = self.args.pop(0).lower()
        except IndexError:
            raise OrganizerExceptions.CommandLineArgumentException('Not enough arguments given')
        if control == 'balance':
            self.balance()
        elif control == 'movedirs':
            self.move_dirs()
        elif control == 'adddir':
            self.add_names_to_files()
        elif control == 'unknown':
            self.unknown_files()
        elif control == 'unknowncontroller':
            self.unknown_interface()
        elif control == 'remove':
            self.remove_files()
        elif control == 'organize':
            self.organize()
        elif control == 'addnames':
            self.add_names()
        elif control == 'testfiles':
            self.create_test_files()
        elif control == 'cachenames':
            self.cache_names()
        else:
            raise  OrganizerExceptions.UnknownArgumentExeption(
                control + ' is not a valid argument. Available args are: '
                + ', ' + str(self.valid_args)
            )
        return None

    def balance(self):
        bal_consts = BalanceConstants()
        # tree_values = [
        #     {
        #         bal_consts.disk_path: '/Volumes/Charlie/',
        #         bal_consts.root_path: '/Volumes/Charlie/t1/'
        #     },
        #     {
        #         bal_consts.disk_path: '/Volumes/Echo/',
        #         bal_consts.root_path: '/Volumes/Echo/t2/',
        #     }
        # ]

        tree_values = [{
                bal_consts.disk_path: '/Volumes/Drummer/',
                bal_consts.root_path: '/Volumes/Drummer/t2/'
            }, {
                bal_consts.disk_path: '/Volumes/IDEAWORKS/',
                bal_consts.root_path: '/Volumes/IDEAWORKS/t1/',
            }
        ]
        balancer = Balancer(tree_values)
        balancer.balance()
        return None

    def move_dirs(self):
        try:
            dst = self.args[0].lower()
        except IndexError:
            raise OrganizerExceptions.CommandLineArgumentException('Must Enter a destination argument.')
        if dst == 'local':
            sourcePath = '/Users/agreen/.stage/finished/organized/'
            #destinationPath = '/Volumes/Echo/.p/finished/'
            destinationPath = '/Volumes/Papa/.finished/organized/'
        elif dst == 'p':
            sourcePath = '/Volumes/Charlie/.p/finished/'
            destinationPath = '/Volumes/Charlie/.p/'
        elif dst == 'papa':
            sourcePath = '/Volumes/Papa/.finished/organized/'
            destinationPath = '/Volumes/Papa/.p/'
        else:
            message = 'Error: ' + dst + ' not a recognized destination. Enter either local or p as destination'
            raise OrganizerExceptions.UnknownArgumentExeption(message)
        start = time.time()
        mover = DirectoryMover(sourcePath, destinationPath)
        mover.move_dirs()
        mover._del_empty_dirs()
        mover.save_recently_moved_names()
        end = time.time()
        minutes = (end - start)/60.
        print('move directories took: %.2f' % minutes, 'minutes')
        return None

    def add_names_to_files(self):
        path = '/Users/agreen/.stage/finished/'
        #path = '/Volumes/Charlie/.p/
        #path = '/Volumes/Papa/.finished/'
        try:
            if len(self.args) == 0:
                raise IndexError
            dir_name = self.args.join(' ')
        except IndexError:
            raise OrganizerExceptions.CommandLineArgumentException('must provide directory name')
        add_names = AddDirNameToFiles(dir_name, path)
        add_names.add()
        return None

    def unknown_files(self):
        path_list = [
            #'/Users/agreen/.stage/finished/organized/',
            '/Volumes/Charlie/.p/',
            '/Volumes/Charlie/.p/finished/',
            '/Volumes/Echo/.p/finished/',
            '/Volumes/Papa/.finished/',
            '/Volumes/Papa/.finished/organized/',
            '/Volumes/Papa/.p/'
            ]
        #path = '/Volumes/Papa/.finished/'
        path = '/Users/agreen/.stage/finished/'
        do_not_print = ['.DS_Store', 'organized', 'music']
        unknown = UnknownFiles(path, path_list, namesNotToPrint=do_not_print, runLocal=False)
        unknown.fetchUnknownFiles()
        unknown.printUnknownFiles()
        unknown.stepThroughFiles()
        return None

    def remove_files(self):
        moveToTop = True
        path = '/Volumes/Charlie/.p/'
        excludedNames = ['random', 'series', 'finished']
        remover = FileRemover(path, ['sample'])
        remover.removeFiles(remover.path)
        if moveToTop:
            mover = FilesToTop(path, excludedNames)
            mover.moveFilesToTop()
        return None

    def organize(self):
        run_first_name = False
        run_from_p = True
        files_to_top = True
        remove_files = True
        top_level_path = "/Users/agreen/.stage/finished/"
        # topLevelPath = '/Volumes/Charlie/.p/finished/'
        #top_level_path = '/Volumes/Papa/.finished/'

        target_path = os.path.join(top_level_path, 'organized')
        excluded_names = ['random', 'series', 'finished']
        names = Names(namesToExclude=excluded_names)
        if run_from_p:
            names.getNamesFromFilesAndDirs([target_path])
        else:
            names.getNamesFromFiles()
        organizerL = Organizer(names, top_level_path, target_path)
        organizerL.moveFilesForFirstAndLastName()
        if run_from_p:
            path_list = [
                '/Volumes/Charlie/.p/',
                '/Volumes/Charlie/.p/finished/',
                '/Volumes/Echo/.p/finished/',
                '/Volumes/Echo/.p/'
            ]
            names.nameList = []
            names.getNamesFromFilesAndDirs(path_list)
            organizerP = Organizer(names, top_level_path, target_path)
            organizerP.moveFilesForFirstAndLastName()
        if run_first_name:
            names.nameList = []
            names.getNamesFromFile()
            organizer1 = Organizer(names, top_level_path, target_path)
            organizer1.moveFilesForFirstName()
        if files_to_top:
            mover = FilesToTop(target_path, excluded_names)
            mover.moveFilesToTop()
        return None

    def add_names(self):
        path = '/Users/agreen/.stage/finished/'
        #path = '/Volumes/Papa/.finished/'
        adder = NameAdder(self.args, path)
        adder.renameFiles()
        return None

    def create_test_files(self):
        file_creator = CreateTestFiles()
        file_creator.create()
        return None

    def cache_names(self):
        path_list = [
            #'/Users/agreen/.stage/finished/organized/',
            '/Volumes/Charlie/.p/',
            '/Volumes/Charlie/.p/finished/',
            '/Volumes/Echo/.p/finished/',
            '/Volumes/Papa/.finished/organized/',
            '/Volumes/Papa/.p/'
            ]
        excluded_names = ['random', 'series', 'finished']
        names = Names(namesToExclude=excluded_names)
        names.updateCachedNames(path_list)
        return None

    def unknown_interface(self):
        path_list = [
            #'/Users/agreen/.stage/finished/organized/',
            '/Volumes/Charlie/.p/',
            '/Volumes/Charlie/.p/finished/',
            '/Volumes/Echo/.p/finished/',
            '/Volumes/Papa/.finished/',
            '/Volumes/Papa/.finished/organized/',
            '/Volumes/Papa/.p/'
            ]
        #path = '/Volumes/Papa/.finished/'
        path = '/Users/agreen/.stage/finished/'
        do_not_print = ['.DS_Store', 'organized', 'music']
        interface = UnknownFilesController(path, path_list, hide=do_not_print)
        interface.run()
        return None

run_organizer = RunOrganizer(sys.argv)
run_organizer.run()