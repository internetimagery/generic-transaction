# File related actions
import os
import time
import shutil

from generic_transaction import Action, Transaction


class FileCreateAction(Action):
    """ Create a file and write data """

    def __init__(self, *_, **__):
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


class FileMoveAction(Action):
    """ Move a file and write data """

    def __init__(self, *_, **__):
        self.source = ""

    def execute(self, action, source, destination):
        shutil.move(source, destination)
        self.source, self.destination = source, destination

    def commit(self):
        pass

    def revert(self):
        if self.source:
            shutil.move(self.destination, self.source)


class FileDeleteAction(Action):
    """ Delete a file """

    def __init__(self, *_, **__):
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

    def __init__(self, *_, **__):
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
Transaction.IO.file.move = FileMoveAction
Transaction.IO.file.delete = FileDeleteAction
Transaction.IO.dir.create = DirCreateAction
Transaction.IO.dir.move = FileMoveAction
Transaction.IO.dir.delete = DirDeleteAction
