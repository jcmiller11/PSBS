# Extensions

PSBS provides the ability to write your own functions and filters in Python.  Extensive documentation of this feature is forthcoming but in the meantime I will include a basic example

Python files can be placed within your project directory and then listed under the user_extensions directive in your config.yaml.  I personally like to place them in a subdirectory I call scripts.

`user_extensions = [scripts/example1.py, scripts/example2.py]`

Extensions must inherit the Extension class of the psbs.extension module.

```Python
from psbs.extension import Extension

class Example(Extension):
    def __init__(self, config):
        super().__init__(config)
        self.register("mycustomfunction", self.mycustomfunction)
        self.register_filter("mycustomfilter", self.mycustomfilter)
        self.register_post(self.mycustompost)

    # including this static method allows you to define custom options to be added to the project's config.yaml
    @staticmethod
    def get_config():
        return {"arrived": True}

    def mycustomfunction(self):
        if self.config("option1")
            output = "Hello world!"
        else
            output = "Goodbye world!"
        return output

    def mycustomfilter(self, input_string):
        # replace questions with excitement
        input_string = input_string.replace("?","!")
        return input_string

    def mycustompost(self, input_string):
        # methods registered with register_post are run after your code has been generated
        # they receive and return the entire output source
        # this will replace all "?"s with "!"s in the entire output source
        return self.mycustomfilter(input_string)

```
