from collections import OrderedDict


class LRUDictCache:
    def __init__(self, max_size=50):
        """
        Initialize the cache with a maximum size.
        :param max_size: Maximum number of dictionaries the cache can hold.
        """
        self.cache = OrderedDict()
        self.max_size = max_size

    def add(self, value):
        """
        Add a dictionary to the cache.
        If the cache exceeds max_size, evict the least recently used entry.
        :param value: The dictionary to store.
        """
        if not isinstance(value, dict):
            raise ValueError("Only dictionaries can be stored in the cache.")

        key = frozenset(value.items())

        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        self.cache[key] = value

    def contains(self, condition):
        """
        Check if any dictionary in the cache satisfies a given condition.
        If a match is found, move it to the most recently used position.
        :param condition: A function that takes a dictionary as input and returns True or False.
        :return: True if at least one dictionary meets the condition, False otherwise.
        """
        for key in list(self.cache.keys()):
            if condition(self.cache[key]):
                self.cache.move_to_end(key)
                return True
        return False

    def find(self, condition):
        """
        Find the first dictionary in the cache that satisfies a given condition.
        Move it to the end (most recently used).
        :param condition: A function that takes a dictionary as input and returns True or False.
        :return: The first dictionary that meets the condition, or None if no dictionary matches.
        """
        for key in list(self.cache.keys()):
            if condition(self.cache[key]):
                self.cache.move_to_end(key)
                return self.cache[key]
        return None

    def remove(self, value):
        """
        Remove a specific dictionary from the cache.
        :param value: The dictionary to remove.
        """
        key = frozenset(value.items())
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """
        Clear the entire cache.
        """
        self.cache.clear()

    def __iter__(self):
        """
        Make the cache iterable, so you can loop through its dictionaries directly.
        """
        return iter(self.cache.values())
