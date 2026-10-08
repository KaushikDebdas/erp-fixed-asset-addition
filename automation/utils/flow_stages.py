"""
flow_stages.py: the base class of every flow that moves through stages (a shipment, a
single challan, ...), so each stage is done once in a full run and every test can
still run alone.

How it works:
    class MyFlow(FlowStages):
        STAGES = {"submit": ["created", "approved"]}      # path -> stages in order

        def do_created(self, path): ...                    # one method per stage: do_<stage>
        def do_approved(self, path): ...

    flow = my_flow.reach("submit", "approved")
    - `reach` does every stage of the path, up to and including the one asked for, that is not
      done yet, and remembers it, so a second test asking for the same stage does nothing.
    - A test that does a stage itself (to check a message, for example) calls `record(path, stage)`
      so the stage is not done twice.
    - `flow(path)` is the dictionary of that path: "done" lists the finished stages, and the stages
      store what later stages need in it (for example "challan_no").
"""
from utils.logger import action_logger


class FlowStages:
    """Does the missing stages of a flow in order and remembers what it did."""

    # Set by each subclass: path name -> list of stage names, in order
    STAGES = {}

    def __init__(self, shared: dict):
        """`shared` is the dictionary shared by the whole test run, one entry per path."""
        self.shared = shared

    def flow(self, path: str) -> dict:
        """Return the remembered flow of this path, empty on first use."""
        return self.shared.setdefault(path, {"done": []})

    def is_done(self, path: str, stage: str) -> bool:
        """Return True when this stage of this path was already done."""
        return stage in self.flow(path)["done"]

    def record(self, path: str, stage: str) -> None:
        """Remember that this stage is done (nothing happens when it is already remembered)."""
        if not self.is_done(path, stage):
            self.flow(path)["done"].append(stage)

    def reach(self, path: str, stage: str) -> dict:
        """Do every stage of `path` up to and including `stage` that is not done yet. Returns the flow dictionary."""
        for name in self.STAGES[path]:
            if not self.is_done(path, name):
                action_logger.info(f"{type(self).__name__} ({path}): doing stage {name}")
                getattr(self, "do_" + name)(path)
                self.record(path, name)
            if name == stage:
                break
        return self.flow(path)
