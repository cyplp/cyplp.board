import couchdbkit

class TypeItem(couchdbkit.Document):
    """
    """
    name = couchdbkit.StringProperty()
    board = couchdbkit.StringProperty()
    color = couchdbkit.StringProperty()
