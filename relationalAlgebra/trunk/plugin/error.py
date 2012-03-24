class CompileError(Exception):
    def __init__(self, value):
        Exception.__init__(self,value)
        self.value = value
    def getValue(self):
        return self.value