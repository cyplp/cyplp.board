import glob
import json
import os.path

from pyramid.events import ApplicationCreated
from pyramid.events import subscriber

import pycouchdb

@subscriber(ApplicationCreated)
def on_launch(event):
    db = event.app.registry.db
    for view in glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*.js')):
        with open(view, 'r') as current:
            doc = json.load(current)
            try:
                db.save(doc)
            except pycouchdb.exceptions.Conflict:
                pass
