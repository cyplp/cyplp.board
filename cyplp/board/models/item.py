import couchdbkit

class Item(couchdbkit.Document):
    """
    """
    title = couchdbkit.StringProperty()
    content = couchdbkit.StringProperty()
    column = couchdbkit.StringProperty()
    board = couchdbkit.StringProperty()
    typeItem = couchdbkit.StringProperty()

    def getType(self):
        try:
            return self.typeItem
        except couchdbkit.exceptions.ResourceNotFound:
            return ''
