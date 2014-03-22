class Relation:
    def __init__(self, header, name):
        self.__header = header
        self.__name = name
        self.__rows = []

    def __iter__(self):
        for i in self.__rows:
            yield i

    def __getitem__(self, key):
        index = []
        for k in key:
            index.append(self.__header.index(k))
        for r in self.__rows:
            row = []
            for i in index:
                row.append(r[i])
            yield row

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def addRow(self,row):
        self.__rows.append(row)

    def getHeader(self):
        return self.__header

    def getLen(self):
        return len(self.__rows)

    def getData(self, i=None, y=None):
        if i is None:
            new = []
            for i in self.__rows:
                new.append(i.getData())
            return new
        else:
            return self.__rows[i].getData(y)

    def getColumn(self, i):
        columns=[]
        for row in self.__rows:
            columns.append(row.getData(i))
        return columns

    def removeColumn(self, column):
        index = self.__header.index(column)
        self.__header.pop(index)
        for data in self.__rows:
            data.pop(index)

    def setRows(self, rows):
        self.__rows = rows

    def getRows(self):
        return self.__rows

class Row:
    def __init__(self,data):
        self.__data=data
    def __iter__(self):
        for i in self.__data:
            yield i
    def getData(self,i=None):
        if i is None:
            return self.__data
        else:
            return self.__data[i]
    def deleteColumn(self,column):
        del self.__data[column]
    def getLen(self):
        return len(self.__data)
    def getString(self):
        string=""
        for i in self.__data:
            string=string+i.__str__()+" "
        return string