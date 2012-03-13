class Row:
    def __init__(self,data,header):
        self.__data=data
        self.__header=header
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
        del self.__header[0][column]
        del self.__header[1][column]
    def getHeader(self):
        return self.__header
    def getLen(self):
        return len(self.__data)