class Extension:
    def __init__(self):
        self.methods = {}

    def register(self, name, function):
        if name not in self.methods:
            self.methods[name] = function
