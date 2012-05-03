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