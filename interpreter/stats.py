class Stats:

    _instance = None
    insts = 0
    hot = ""
    vars = 0

    def __new__(self):
        """
        Initiates Stats class object (is a singleton)
        """
        if not self._instance:
            self._instance = super(Stats, self).__new__(self)
        return self._instance