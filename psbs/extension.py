class Extension:
    def __init__(self, config):
        self.methods = {}
        self.config = config
        if self.get_config():
            for key, value in self.get_config().items():
                if not key in self.config:
                    self.config[key] = None
                if not self.config[key]:
                    self.config[key] = value

    def register(self, name, function):
        if name not in self.methods:
            self.methods[name] = function

    @staticmethod
    def get_config():
        return None
