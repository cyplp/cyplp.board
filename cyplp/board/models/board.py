import couchdbkit

class Board(couchdbkit.Document):
    """
    """
    title = couchdbkit.StringProperty()
    owner = couchdbkit.StringProperty()
