import couchdbkit

class Item(couchdbkit.Document):
    """
    """
    title = couchdbkit.StringProperty()
    content = couchdbkit.StringProperty()
    column = couchdbkit.StringProperty()
    board = couchdbkit.StringProperty()
    typeItem = couchdbkit.StringProperty()
    tags = couchdbkit.StringListProperty()

    def getType(self):
        try:
            return self.typeItem
        except couchdbkit.exceptions.ResourceNotFound:
            return ''

    def getTags(self):
        try:
            return self.tags
        except couchdbkit.exceptions.ResourceNotFound:
            return []
