import json
import threading
from arcjetCV.utils.utils import splitfn, NumpyEncoder


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
        folder, name, ext = splitfn(path)
        self.folder = folder
        self._lock = threading.Lock()

        namesplit = name.split('_')
        self.prefix = namesplit[0:-2]
        self.low_index = int(namesplit[-2])
        self.high_index = int(namesplit[-1])

    def write(self):
        with self._lock:
            json_object = json.dumps(self, indent=4, cls=NumpyEncoder)
            # Writing to sample.json
            with open(self.path, "w") as outfile:
                outfile.write(json_object)

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
