__author__ = 'Michal'

from Product import Product
from Projection import Projection
from Difference import Difference
import copy
from error import CompileError
from relation import Relation

class Division:
    def __init__(self):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__name = "Division"
        self.__element = None
        self.__data = None

    def set(self,ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left = ancestor
        else:
            self.__ancestor_right = ancestor

    def paint(self, interface, diagram):
        connection_left = interface.project.metamodel.connections["Relationship"]
        connection_right = interface.project.metamodel.connections["Relationship"]
        ancestor_element_left = self.__ancestor_left.paint(interface, diagram)
        ancestor_element_right = self.__ancestor_right.paint(interface, diagram)
        el = self.create_element(interface, diagram)
        ancestor_element_left.connect_with(el, connection_left)
        ancestor_element_right.connect_with(el, connection_right)
        return el

    def create_element(self, interface, diagram):
        if self.__element is None:
            element = interface.project.metamodel.elements[self.__name]
            el = diagram.create_element(element)
            self.__element = el
        return self.__element

    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        columns=ret.getHeader()
        columns_help=copy.deepcopy(columns)
        columns1=ret1.getHeader()
        indexes=[]
        indexes2=[]
        match={}
        #ulozi do premennej indexes cisla stlpcov, ktore treba delit
        for i in range(0,len(columns1)):
            try:
                indexes.append(self.findElement(columns,columns1[i]))
                del columns[indexes[-1]]
            except ValueError:
                raise CompileError("Columns`s names are not founded in table","Division error in "+self.__name)
        relation=Relation(columns,self.__name)
        #ulozi do premennej indexes2 cisla stlpcov, ktore ostanu vo vyslednej relacii
        for i in range(0,len(columns)):
            indexes2.append(self.findElement(columns_help,columns[i]))
        #pre vsetky riadky v relacii zostavy string zo stlpcov, ktorymi delime, a ulozi do premennej match novy zaznam
        #ak este zaznam neexistuje v premmenej matches alebo zvysi pocet najdenych zaznamov o jedna ak sa tam uz nachadza
        for i in ret :
            string1=""
            for a in range(0,len(indexes)):
                string1=string1+","+ i[indexes[a]]
            for y in ret1:
                string2=""
                for b in range(0,len(indexes)):
                    string2=string2+","+y[b]
                if string1==string2:
                    string3=""
                    for c in range(0,len(indexes2)):
                        string3=string3+","+i[(indexes2[c])].__str__()
                    if match.get(string3) is None :
                        new= [string3, 1]
                        match[string3]=new
                    else:
                        new=match.get(string3)
                        number=new[1]
                        new[1]=number+1
                        match[string3]=new
        #vyberie vsetky hodnoty
        values=match.values()
        #pre vsetky hodnoty skontroluje, ktorej hodnoty sa pocet rovna poctu riadkov, ktorymi sme delili
        #pre tu ktora vyhovuje rozdeli jej hodnotu podla ciarky na stlpce a vytvori novy Row s tymito hodnotami a nasledne
        #prida do relacie
        for i in range(0,len(values)):
            new=values[i]
            if new[1]== ret1.getLen():
                row=new[0]
                new1=row.rsplit(",")
                row=[]
                for y in range(0,len(new1)):
                    if y is not 0:
                        row.append(new1[y])
                relation.addRow(row)
        return relation

    def findElement(self, array,data):
        for i in range(0,len(array)):
            try:
                index=array[i].index(data)
                return i
            except ValueError:
                pass
        raise ValueError