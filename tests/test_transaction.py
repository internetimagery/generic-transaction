
import unittest
from collections import defaultdict

from clean_transaction import Action, Transaction

counter = defaultdict(int)

class Success(Action):
    def execute(self, _, *_, **__):
        counter["execute"] += 1
    def commit(self):
        counter["commit"] += 1
    def revert(self):
        counter["revert"] += 1

class FailInit(Success):
    def __init__(self):
        raise RuntimeError()

class FailExecute(Success):
    def execute(self, *args):
        super(FailExecute, self).execute(*args)
        raise RuntimeError()

class FailRevert(Success):
    def revert(self):
        super(FailRevert, self).revert()
        raise RuntimeError()

class FailCommit(Success):
    def commit(self):
        super(FailCommit, self).commit()
        raise RuntimeError()

Transaction.test.success = Success
Transaction.test.init = FailInit
Transaction.test.execute = FailExecute
Transaction.test.revert = FailRevert
Transaction.test.commit = FailCommit

class TestTransactionRuntime(unittest.TestCase):

    def setUp(self):
        counter.clear()

    def test_success(self):
        with Transaction() as action:
            action.test.success()
            action.test.success()
            action.test.success()

        self.assertEqual(counter["execute"], 3)
        self.assertEqual(counter["commit"], 3)
        self.assertEqual(counter["revert"], 0)

    def test_rollback(self):
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.test.success()
                action.test.success()
                action.test.success()
                raise RuntimeError()

        self.assertEqual(counter["execute"], 3)
        self.assertEqual(counter["commit"], 0)
        self.assertEqual(counter["revert"], 3)

    def test_fail_init(self):
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.test.success()
                action.test.init()
                action.test.success()

        self.assertEqual(counter["execute"], 1)
        self.assertEqual(counter["commit"], 0)
        self.assertEqual(counter["revert"], 1)

    def test_fail_execute(self):
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.test.success()
                action.test.execute()
                action.test.success()

        self.assertEqual(counter["execute"], 2)
        self.assertEqual(counter["commit"], 0)
        self.assertEqual(counter["revert"], 2)

    def test_fail_commit(self):
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.test.success()
                action.test.commit()
                action.test.success()

        self.assertEqual(counter["execute"], 3)
        self.assertEqual(counter["commit"], 2)
        self.assertEqual(counter["revert"], 1)

    def test_fail_revert(self):
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.test.success()
                action.test.revert()
                action.test.success()
                raise RuntimeError()

        self.assertEqual(counter["execute"], 3)
        self.assertEqual(counter["commit"], 0)
        self.assertEqual(counter["revert"], 3)

class TestTransactionMisc(unittest.TestCase):

    def test_bad_assign(self):
        with self.assertRaises(TypeError):
            Transaction.doesnt = "work"

    def test_shallow_assign(self):
        Transaction.shallow = Success
        with Transaction() as action:
            action.shallow()

    def test_deep_assign(self):
        Transaction.this.very.deep.so.deep.my.gosh = Success
        with Transaction() as action:
            action.this.very.deep.so.deep.my.gosh()

    def test_out_of_scope(self):
        with self.assertRaises(RuntimeError):
            Transaction().test.success()
        with self.assertRaises(RuntimeError):
            with Transaction() as action:
                action.test.success()
            action.test.success()


if __name__ == '__main__':
    unittest.main()
