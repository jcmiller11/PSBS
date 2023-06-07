class Config(dict):
    def __getitem__(self, key):
        try:
            return super(Config, self).__getitem__(key)
        except KeyError as err:
            print(f"Error: Unable to find {err} directive in config file")
            raise SystemExit(1) from err