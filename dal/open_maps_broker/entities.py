class PartialNodeInfo(Exception):
    def __init__(self, message, node):
        self.message = message
        self.node = node

    def __str__(self):
        return "API returned a partial node info"
