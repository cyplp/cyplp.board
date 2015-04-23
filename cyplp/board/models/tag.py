import couchdbkit

class Tag(couchdbkit.Document):
    """
    """
    name = couchdbkit.StringProperty()
    board = couchdbkit.StringProperty()
    color = couchdbkit.StringProperty()
