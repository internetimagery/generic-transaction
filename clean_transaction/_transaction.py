import abc
import os.path
import logging
import traceback
import threading

# Spec:
    # An action can contain other actions (provided they use the instance passed into the function)
    # An Error within the scope will cause all actions to revert.
    # An Error within an actions execute will cause it (and the stack) to revert. It needs to manage its state.
    # An Error within an actions commit will cause the stack to revert to that point.
    # An Error within an actions revert will be printed, but will not shadow the main error.

LOG = logging.getLogger(__name__)

class Action(object):
    """ Single "atomic" state change """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self, action):
        """
        Perform the action.
        Must maintain state, and be mindful of a potential undo.
        """
        pass

    @abc.abstractmethod
    def revert(self):
        """
        Restore the previous state.
        It's important this action is as simple and fault free as possible.
        """
        pass

    @abc.abstractmethod
    def commit(self):
        """
        Finalize/Cleanup the action.
        Preferably this operation (if any) should be genuinely atomic.
        """
        pass


# TODO: Rework this metaclass to be compatibile with python3

class Transaction(object):
    """
    Generate a transaction scope. All actions within the scope should finish
    successfully or else will undo themselves, and revert state safely.
    """

    __actions__, __scoped__ = {}, False

    class __metaclass__(type):

        __path__ = __root__ = ''

        def __getattr__(self, attr):
            return Transaction(self.__root__ or self, os.path.join(self.__path__, attr))

        def __setattr__(self, attr, action):
            if attr.startswith("__"):
                return super(type(self), self).__setattr__(attr, action)
            if not issubclass(action, Action):
                raise TypeError("Only Actions may be registered. Got {}".format(action))
            self.__actions__[os.path.join(self.__path__, attr)] = action

    __getattr__ = __metaclass__.__getattr__.__func__
    __setattr__ = __metaclass__.__setattr__.__func__

    def __init__(self, root=None, path=''):
        self.__root__, self.__path__ = root, path

    def __call__(self, *args, **kwargs):
        if not self.__root__:
            raise TypeError("'{}' object is not callable".format(type(self).__name__))
        if not self.__root__.__scoped__:
            raise RuntimeError("Cannot execute actions outside of scope.")
        with self.__root__.__lock__:
            action = self.__actions__[self.__path__]()
            self.__root__.__queue__.append(action)
        return action.execute(self.__root__, *args, **kwargs)

    def __enter__(self):
        self.__queue__, self.__lock__, self.__scoped__ = [], threading.Lock(), True
        return self

    def __exit__(self, err, *_):
        with self.__lock__:
            self.__scoped__ = False
            try:
                while not err and self.__queue__:
                    self.__queue__.pop(0).commit()
            finally:
                for action in reversed(self.__queue__):
                    try:
                        action.revert()
                    except Exception:
                        LOG.error(traceback.format_exc())

if __name__ == '__main__':

    # Create a new action.
    class PrintAction(Action):
        def execute(self, action, msg):
            LOG.info("RUNNING", msg)
        def revert(self):
            LOG.info("REVERT")
        def commit(self):
            LOG.info("COMMIT")

    # Register the action for use, nested any level deep.
    Transaction.some.category.printer = PrintAction

    # Run actions within a transaction scope.
    with Transaction() as action:
        LOG.info("== Successful ==")
        action.some.category.printer("SUCCESS")

    try:
        # A failed transaction will cause the actions to revert.
        with Transaction() as action:
            LOG.info("=== Failure ====")
            action.some.category.printer("FAILURE")
            raise RuntimeError()
    except RuntimeError:
        pass
