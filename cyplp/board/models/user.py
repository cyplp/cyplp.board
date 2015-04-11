import couchdbkit

class User(couchdbkit.Document):
    """
    """
    name = couchdbkit.StringProperty()
    password = couchdbkit.StringProperty()
    admin = couchdbkit.BooleanProperty()
