
import shutil
import unittest
import tempfile
import os.path

from generic_transaction import Transaction
import generic_transaction.actions.IO


class Tempfile(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)


class TestIOFile(Tempfile):

    def test_file_create(self):
        path = os.path.join(self.tempdir, "file1.txt")
        with Transaction() as action:
            action.IO.file.create(path, "someinfo")
        self.assertTrue(os.path.isfile(path))

        path = os.path.join(self.tempdir, "file2.txt")
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.IO.file.create(path, "someinfo")
                raise RuntimeError()
        self.assertFalse(os.path.isfile(path))

    def test_file_move(self):
        path1 = os.path.join(self.tempdir, "file1.txt")
        path2 = os.path.join(self.tempdir, "file2.txt")
        with open(path1, "w") as f: f.write("hi")
        with Transaction() as action:
            action.IO.file.move(path1, path2)
        self.assertTrue(os.path.isfile(path2))
        self.assertFalse(os.path.exists(path1))

        path3 = os.path.join(self.tempdir, "file3.txt")
        path4 = os.path.join(self.tempdir, "file4.txt")
        with open(path3, "w") as f: f.write("hi")
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.IO.file.move(path3, path4)
                raise RuntimeError()
        self.assertTrue(os.path.isfile(path3))
        self.assertFalse(os.path.exists(path4))

    def test_file_delete(self):
        path = os.path.join(self.tempdir, "file1.txt")
        with open(path, "w") as f: f.write("hi")
        with Transaction() as action:
            action.IO.file.delete(path)
        self.assertFalse(os.path.exists(path))

        path = os.path.join(self.tempdir, "file2.txt")
        with open(path, "w") as f: f.write("hi")
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.IO.file.delete(path)
                raise RuntimeError()
        self.assertTrue(os.path.isfile(path))


class TestIODir(Tempfile):

    def test_dir_create(self):
        path = os.path.join(self.tempdir, "dir1")
        with Transaction() as action:
            action.IO.dir.create(path)
        self.assertTrue(os.path.isdir(path))

        path = os.path.join(self.tempdir, "dir2")
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.IO.dir.create(path)
                raise RuntimeError()
        self.assertFalse(os.path.exists(path))

    def test_dir_move(self):
        path1 = os.path.join(self.tempdir, "dir1")
        path2 = os.path.join(self.tempdir, "dir2")
        os.mkdir(path1)
        with Transaction() as action:
            action.IO.dir.move(path1, path2)
        self.assertTrue(os.path.isdir(path2))
        self.assertFalse(os.path.exists(path1))

        path3 = os.path.join(self.tempdir, "dir3")
        path4 = os.path.join(self.tempdir, "dir4")
        os.mkdir(path3)
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.IO.dir.move(path3, path4)
                raise RuntimeError()
        self.assertTrue(os.path.isdir(path3))
        self.assertFalse(os.path.exists(path4))

    def test_dir_delete(self):
        path = os.path.join(self.tempdir, "dir1")
        os.mkdir(path)
        with Transaction() as action:
            action.IO.dir.delete(path)
        self.assertFalse(os.path.exists(path))

        path = os.path.join(self.tempdir, "dir2")
        os.mkdir(path)
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.IO.dir.delete(path)
                raise RuntimeError()
        self.assertTrue(os.path.isdir(path))


if __name__ == '__main__':
    unittest.main()
