import json
import threading
import numpy as np
import datetime
from arcjetCV.utils.utils import splitfn


class NumpyEncoder(json.JSONEncoder):
    '''
    JSON encoder for NumPy arrays.

    This class extends the JSONEncoder class to handle NumPy arrays, converting them to lists before encoding.

    Example:
    ```python
    encoder = NumpyEncoder()
    encoded_array = encoder.encode(numpy_array)
    ```

    Attributes:
        None
    '''

    def default(self, obj):
        """
        Convert NumPy arrays to lists for JSON serialization.

        :param obj: Object to encode.
        :returns: Encoded object.
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.__str__()
        return json.JSONEncoder.default(self, obj)


class OutputListJSON(list):
    '''
    Extension of list with write to file function, expected to hold dictionary objects corresponding to analysis of individual video frames.

    This class extends the list class and provides a method to write its contents to a JSON file. It is designed to hold dictionaries corresponding to the analysis of individual video frames. The filename must contain low and high index constraints delimited by underscores, e.g., "myoutput_0_10.json".

    Args:
        list (list): Base list class.
        filepath (str): Path for saving file.

    Example:
    ```python
    output_list = OutputListJSON('output.json')
    output_list.append({'INDEX': 0, 'data': 'some_data'})
    output_list.write()
    ```

    Attributes:
        path (str): Path to the JSON file.
        folder (str): Directory containing the JSON file.
        _lock (threading.Lock): Threading lock for thread-safe operations.
        prefix (list): Prefix extracted from the filename.
        low_index (int): Low index constraint extracted from the filename.
        high_index (int): High index constraint extracted from the filename.
    '''

    def __init__(self,path):
        """
        Initializes the OutputListJSON object.

        :param path: Path for saving file.
        """
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
        """
        Writes the list to a JSON file.

        :param indent: Number of spaces for indentation (default=None).
        """
        with self._lock:
            json_object = json.dumps(self, indent=indent, cls=NumpyEncoder)
            # Writing to sample.json
            with open(self.path, "w") as outfile:
                outfile.write(json_object)

            print("\n\nEdges output written to", self.path)

    def load(self,path,extend=True):
        """
        Loads data from a JSON file.

        :param path: Path to the JSON file.
        :param extend: Whether to extend the current list with the loaded data (default=True).
        :returns: Loaded data.
        """
        with self._lock:
            with open(path,'r') as fin:
                dload = json.load(fin)
                if extend:
                    self.extend(dload)
                return dload

    def append(self,obj):
        """
        Appends an object to the list if its INDEX is within the specified range.

        :param obj: Object to append.
        """
        with self._lock:
            if obj["INDEX"] <= self.high_index and obj["INDEX"] >= self.low_index:
                super(OutputListJSON,self).append(obj)
