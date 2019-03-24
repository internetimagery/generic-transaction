# File related actions
import os
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

Transaction.IO.file.create = FileCreateAction
Transaction.IO.dir.create = DirCreateAction
