from collections import OrderedDict
def data_maker(d):
    l = []
    keys = list(d.keys())
    test_len = None
    for key in keys:
        assert isinstance(d[key], list)
        if test_len == None:
            test_len = len(d[key])
        else:
            assert len(d[key]) == test_len
    for counter, i in enumerate(d[keys[0]]):
        temp = []
        for j in keys:
            temp.append((j, d[j][counter]))
        temp = OrderedDict(temp)
        l.append(temp)
    return l

class MockQeryJob:

    def __init__(self, ordered_dict, job_id = 1, running = False, errors = None):
        if isinstance(ordered_dict, dict):
            ordered_dict = data_maker(ordered_dict)
        self.ordered_dict = ordered_dict
        self._index = -1
        self.job_id = job_id
        self._running = running
        self.errors = errors

    def __iter__(self):
        return self

    def __next__(self): 
        self._index += 1
        try:
            self.ordered_dict[self._index]
            return self
        except IndexError:
            raise StopIteration
        except KeyError:
            raise StopIteration

    def items(self):
        for key, value in self.ordered_dict[self._index].items():
            yield (key, value)

    def running(self, *args, **kwargs):
        return self._running

    def values(self):
        """
        returns just the values, without keys
        """
        return tuple([x[1]  for x in self.ordered_dict[self._index].items()])

    def result(self):
        pass

    def get(self, key):
        """
        returns the value of the dict:
        use the columns name
        get(order_id)
        """
        d =  self.ordered_dict[self._index]
        return d.get(key)

    def keys(self):
        """
        returns iterator of keys of dict
        """
        for i in self.ordered_dict[self._index].keys():
            yield i
