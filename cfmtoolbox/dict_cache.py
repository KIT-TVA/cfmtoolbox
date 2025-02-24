class DictCache:
    def __init__(self, max_size=50):
        """
        Initialize the cache with a maximum size.
        :param max_size: Maximum number of dictionaries the cache can hold.
        """
        self.cache = []
        self.max_size = max_size

    def add(self, value):
        """
        Add a dictionary to the cache.
        If the cache exceeds max_size, evict the oldest entry.
        :param value: The dictionary to store.
        """
        if not isinstance(value, dict):
            raise ValueError("Only dictionaries can be stored in the cache.")

        if value in self.cache:
            # Move existing dictionary to the end (most recently added)
            self.cache.remove(value)
        elif self.max_size and len(self.cache) >= self.max_size:
            # Evict the oldest entry if at max size
            self.cache.pop(0)

        # Add the new dictionary
        self.cache.append(value)

    def contains(self, condition):
        """
        Check if any dictionary in the cache satisfies a given condition.
        :param condition: A function that takes a dictionary as input and returns True or False.
        :return: True if at least one dictionary meets the condition, False otherwise.
        """
        return any(condition(entry) for entry in self.cache)

    def find(self, condition):
        """
        Find the first dictionary in the cache that satisfies a given condition.
        :param condition: A function that takes a dictionary as input and returns True or False.
        :return: The first dictionary that meets the condition, or None if no dictionary matches.
        """
        for entry in self.cache:
            if condition(entry):
                return entry
        return None

    def remove(self, value):
        """
        Remove a specific dictionary from the cache.
        :param value: The dictionary to remove.
        """
        if value in self.cache:
            self.cache.remove(value)

    def clear(self):
        """
        Clear the entire cache.
        """
        self.cache.clear()

    def __iter__(self):
        """
        Make the cache iterable, so you can loop through its dictionaries directly.
        """
        return iter(self.cache)
