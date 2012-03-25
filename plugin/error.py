class CompileError(Exception):
    def __init__(self, value,name):
        Exception.__init__(self,value,name)
        self.name=name
        self.value = value
    def getValue(self):
        return self.value
    def getName(self):
        return self.name