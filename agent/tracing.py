"""Real execution trace: wraps every tool so the UI shows what the agent ACTUALLY did."""
import functools
import json
import time


class Trace:
    def __init__(self):
        self.steps = []

    def wrap(self, fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            t0 = time.time()
            status = "ok"
            try:
                out = fn(*args, **kwargs)
            except Exception as e:  # surface error to the model so it can recover
                out, status = {"error": f"{type(e).__name__}: {e}"}, "error"
            self.steps.append({"step": len(self.steps) + 1, "tool": fn.__name__, "args": kwargs or list(args),
                               "status": status, "latency_s": round(time.time() - t0, 2),
                               "result_preview": json.dumps(out, default=str)[:600]})
            return out
        return inner
