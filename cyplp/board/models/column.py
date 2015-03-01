import couchdbkit

class Column(couchdbkit.Document):
    """
    """
    title = couchdbkit.StringProperty()
    board = couchdbkit.StringProperty()
