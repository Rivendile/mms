"""Common utilities."""
import logging
from functools import partial
from typing import Sequence, Any

import ray

GB = 1 << 30

def build_logger(name="alpa_serve"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger


def add_sync_method(actor, method_names):
    """Add a actor.sync method to wait for all calls to methods
    listed in method_names."""
    calls = []

    def sync():
        ray.get(calls)
        calls.clear()

    setattr(actor, "sync", sync)

    for name in method_names:
        attr = getattr(actor, name)
        old_remote = attr.remote
        setattr(attr, "remote", partial(wrapped_remote_call, old_remote, calls))


def wrapped_remote_call(old_remote, calls, *args, **kwargs):
    ret = old_remote(*args, *kwargs)
    calls.append(ret)
    return ret


def write_tsv(heads: Sequence[str],
              values: Sequence[Any],
              filename: str,
              print_line: bool = True):
    """Write tsv data to a file."""
    assert len(heads) == len(values)

    values = [str(x) for x in values]

    with open(filename, "a", encoding="utf-8") as fout:
        fout.write("\t".join(values) + "\n")

    if print_line:
        line = ""
        for i in range(len(heads)):
            line += heads[i] + ": " + values[i] + "  "
        print(line)
