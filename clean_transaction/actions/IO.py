# File related actions
import os
import time
import shutil

from clean_transaction import Action, Transaction


class FileCreateAction(Action):
    """ Create a file and write data """

    def __init__(self):
        self.path = ""

    def execute(self, action, path, data, binary=False):
        with open(path, "wb" if binary else "w") as handle:
            self.path = path
            handle.write(data)

    def commit(self):
        pass

    def revert(self):
        if self.path:
            os.remove(self.path)

class FileDeleteAction(Action):
    """ Delete a file """

    def __init__(self):
        self.path = ""
        self.temp = ""

    def execute(self, action, path):
        self.path = path
        while True:
            temp = path + str(int(time.time()))
            if not os.path.exists(temp):
                shutil.move(path, temp)
                self.temp = temp
                break

    def commit(self):
        os.remove(self.temp)

    def revert(self):
        if self.temp:
            shutil.move(self.temp, self.path)


class DirCreateAction(Action):
    """ Create a directory """

    def __init__(self):
        self.path = ""

    def execute(self, action, path):
        os.mkdir(path)
        self.path = path

    def commit(self):
        pass

    def revert(self):
        if self.path:
            shutil.rmtree(self.path)


class DirDeleteAction(FileDeleteAction):
    """ Delete a directory """

    def commit(self):
        shutil.rmtree(self.temp)


Transaction.IO.file.create = FileCreateAction
Transaction.IO.file.delete = FileDeleteAction
Transaction.IO.dir.create = DirCreateAction
Transaction.IO.dir.delete = DirDeleteAction
