import couchdbkit

class Item(couchdbkit.Document):
    """
    """
    title = couchdbkit.StringProperty()
    content = couchdbkit.StringProperty()
    column = couchdbkit.StringProperty()
    board = couchdbkit.StringProperty()
