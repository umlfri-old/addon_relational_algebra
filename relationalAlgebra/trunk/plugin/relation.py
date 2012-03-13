class Relation:
    def __init__(self,header):
        self.__header=header
        self.__rows=[]
    def __iter__(self):
        for i in self.__rows:
            yield i
    def addRow(self,row):
        self.__rows.append(row)
    def getHeader(self):
        return self.__header
    def getColumnsName(self):
        return self.__header[0]
    def getLen(self):
        return len(self.__rows)
    def getData(self):
        new=[]
        for i in self.__rows:
            new.append(i.getData())
        return new