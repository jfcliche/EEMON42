""" Module that defines the namespace class
"""
class Namespace(dict):
    """ Dict class that allows its items to be accessed as attributes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # recursively convert dicts objects into Namespace 
        for k,v in self.items():
            if isinstance(v, dict):
                self[k] = Namespace(v)
            elif isinstance(v, list):
                for i,vv in enumerate(v):
                    if isinstance(vv, dict):
                        v[i] = Namespace(vv)
    def __getattr__(self, name):
        return self[name]
    def __setattr__(self, name, value):
        self[name] = value
