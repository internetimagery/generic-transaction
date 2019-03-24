# generic-transaction

A generic transaction framework to enable simple executions of "safe" actions that know how
to clean up after themselves.

eg

``` python
import generic_transaction.actions.IO # Initialize IO actions
from generic_transaction import Transaction
```
``` python
with Transaction() as action: # Perform actions and logic in a scope
    action.IO.dir.create(dirpath)
    # Some logic ...
    action.IO.file.create(filepath, somedata)
```
...or...

```python
action = Transaction()
action.start() # Perhaps we zip off to some thread somewhere?...
try:
    action.ID.file.create(filepath)
    action.IO.file.delete(filepath)
except Exception:
    action.end(True)
else:
    action.end(False)
```

## Actions

Transactions provide the scope. Actions provide the fuctionality. The building blocks.
Each action is described with an "execute", "revert", and "commit" function.

``` python
from generic_transaction import Action, Transaction
class MyAction(Action):
    def execute(self, action):
        pass
    def commit(self):
        pass
    def revert(self):
        pass
# Register the action for usage later
Transaction.path.to.my.action = MyAction
```

### Execute

Execute is expected to perform 90-100% of the actions' functionality. If errors are to happen, they should
ideally happen here. When running, one must be mindful of the current state, in case an error occurrs and
the cleanup in revert needs to know what to clean.

### Commit

This will be run after all executions and the entire transaction scope has completed and no errors were raised.
Use this time to perform any last minute cleanup, or changes to lock things in.
Perferrably no errors should occur here.

### Revert

If an error was raised within the transaction scope, in the execute functions or in the commit pass, we will start reverting.
The expectation is to return the state back as it was when the execute step above began.
As this is only ever run while another error is being processed, it is a good idea to keep this as simple and error
free as possible. Errors within this step will be logged, but not raised.
All reverts on all actions will have a chance to run, regardless of their failings.

## Nesting

Nested actions are possible (and thus larger grouped meta-actions), by using the passed in "action" instance,
belonging to the currently running scope.
If an error occurrs, cleanup of the inner actions will happen before the outer action.

``` python
class MyComplexAction(Action):
    def execute(self, action):
        # some logic
        action.some.action()
        action.some.other.action()
        # logic logic etc
    ...
```

For examples and existing actions have a look at

```
generic_transaction.actions
```

If you wish to contribute more actions or any kind of patch/code/feedback, feel free!

Best Wishes!
