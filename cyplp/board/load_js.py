import glob
import json
import os.path

from pyramid.events import ApplicationCreated
from pyramid.events import subscriber


@subscriber(ApplicationCreated)
def on_launch(event):
    db = event.app.registry.db

    for view in glob.glob(os.path.join(os.path.dirname(__file__), 'data', '*.js')):
        with open(view, 'r') as current:
            doc = json.load(current)
            db.save(doc)
