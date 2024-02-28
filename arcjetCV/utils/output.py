import json
import threading
import numpy as np
from arcjetCV.utils.utils import splitfn


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.uint8) or isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return json.JSONEncoder.default(self, obj)


class OutputListJSON(list):
    """Extension of list with write to file function
        expected to hold dictionary objects corresponding to
        analysis of individual video frames

        filepath argument must contain low and high index constraints
        which are delimited by underscores:
        e.g. myoutput_0_10.json

    Args:
        list (list): base list class
        filepath (string): path for saving file
    """

    def __init__(self,path):
        super(OutputListJSON,self).__init__()
        self.path=path
        folder, name, _ = splitfn(path)
        self.folder = folder
        self._lock = threading.Lock()

        namesplit = name.split('_')
        self.prefix = namesplit[0:-2]
        self.low_index = int(namesplit[-2])
        self.high_index = int(namesplit[-1])

    def write(self, indent=None):
        with self._lock:
            json_object = json.dumps(self, indent=indent, cls=NumpyEncoder)
            # Writing to sample.json
            with open(self.path, "w") as outfile:
                outfile.write(json_object)
            print("Edges output written to", self.path)

    def load(self,path,extend=True):
        with self._lock:
            with open(path,'r') as fin:
                dload = json.load(fin)
                if extend:
                    self.extend(dload)
                return dload

    def append(self,obj):
        with self._lock:
            if obj["INDEX"] <= self.high_index and obj["INDEX"] >= self.low_index:
                super(OutputListJSON,self).append(obj)
