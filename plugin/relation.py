class Relation:
    def __init__(self,header,name):
        self.__header=header
        self.__name=name
        self.__rows=[]
    def __iter__(self):
        for i in self.__rows:
            yield i
    def getName(self):
        return self.__name
    def addRow(self,row):
        self.__rows.append(row)
    def getHeader(self):
        return self.__header
    def getColumnsName(self):
        return self.__header[0]
    def getLen(self):
        return len(self.__rows)
    def getData(self,i=None,y=None):
        if i is None:
            new=[]
            for i in self.__rows:
                new.append(i.getData())
            return new
        else:
            return self.__rows[i].getData(y)
    def getColumn(self,i):
        columns=[]
        for row in self.__rows:
            columns.append(row.getData(i))
        return columns