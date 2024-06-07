class PartialNodeInfo(Exception):
    def __init__(self, message, node):
        super().__init__(message)
        self.node = node

    def __str__(self):
        return "API returned a partial node info"
