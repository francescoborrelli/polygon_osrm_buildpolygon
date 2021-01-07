#  Copyright (c) 2020. AV Connect Inc.
import contextlib
from data import models
import os



# DB utils.  Clear db table
def clear_tables(engine):
    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(models.Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()

# redis mock data
data = {}
def set(key, val):
    data[key] = val

def get(key):
    return data[key]
