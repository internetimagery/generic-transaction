import abc
import os.path
import logging
import traceback
import threading

__all__ = ("Action", "Transaction")

# Spec:
    # An action can contain other actions (provided they use the instance passed into the function)
    # An Error within the scope will cause all actions to revert.
    # An Error within an actions execute will cause it (and the stack) to revert. It needs to manage its state.
    # An Error within an actions commit will cause the stack to revert to that point.
    # An Error within an actions revert will be printed, but will not shadow the main error.

LOG = logging.getLogger(__name__)

def metaclass(meta):
    """ Metaclass for python 2 & 3 """
    try:
        exec("class Dummy(object, metaclass=meta): pass", locals())
    except SyntaxError:
        exec("class Dummy(object): __metaclass__ = meta", locals())
    return locals()["Dummy"]

class Action(metaclass(abc.ABCMeta)):
    """ Single "atomic" state change """

    def __init__(self, *args, **kwargs):
        pass

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

def getter(self, attr):
    return Transaction(*self.__context__[0], **self.__context__[1]).__chain__(
        self.__root__ or self, os.path.join(self.__path__, attr))


def setter(self, attr, action):
    if attr.startswith("__"):
        return super(type(self), self).__setattr__(attr, action)
    if not self.__path__ and attr in dir(self):
        raise AttributeError("can't set attribute")
    if not issubclass(action, Action):
        raise TypeError("Only Actions may be registered. Got {}".format(action))
    self.__actions__[os.path.join(self.__path__, attr)] = action

class TransactionMeta(type):
    __context__ = ([],{})
    __path__ = __root__ = ''
    __getattr__, __setattr__ = getter, setter

class Transaction(metaclass(TransactionMeta)):
    """
    Generate a transaction scope. All actions within the scope should finish
    successfully or else will undo themselves, and revert state safely.
    """

    __actions__, __scoped__ = {}, False
    __getattr__, __setattr__ = getter, setter

    def __init__(self, *args, **kwargs):
        self.__context__ = (args, kwargs)
        self.__root__ = self.__path__ = ""

    def __chain__(self, root, path):
        self.__root__, self.__path__ = root, path
        return self

    def __call__(self, *args, **kwargs):
        if not self.__root__:
            raise TypeError("'{}' object is not callable".format(type(self).__name__))
        if not self.__root__.__scoped__:
            raise RuntimeError("Cannot execute actions outside of scope.")
        with self.__root__.__lock__:
            action = self.__actions__[self.__path__](*self.__context__[0], **self.__context__[1])
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

    @property
    def start(self):
        return self.__enter__

    @property
    def end(self):
        return self.__exit__
