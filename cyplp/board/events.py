class ItemMoved(object):
    """
    """
    def __init__(self, item, fromColumn, toColumn):
        self.item = item
        self.fromColumn = fromColumn
        self.toColumn = toColumn

class ItemEdit(object):
    def __init__(self, item):
        self.item = item
