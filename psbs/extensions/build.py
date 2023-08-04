from psbs.extension import Extension


class Build(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register("build", self.get_build)
        self.register("debug", self.is_debug)
        self.register("release", self.is_release)

    @staticmethod
    def get_config():
        return {"name": "debug"}

    def get_build(self):
        return self.config["name"]

    def is_debug(self):
        return self.config["name"].lower() == "debug"

    def is_release(self):
        return self.config["name"].lower() == "release"
