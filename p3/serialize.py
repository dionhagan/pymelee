import json

class Serializer:
    def __init__(self, obj):
        self.obj = obj
    def toJSON(self):
        return json.dumps(self.obj, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
