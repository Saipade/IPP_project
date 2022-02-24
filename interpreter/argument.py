import xml.etree.ElementTree as ET

class Argument: 

    def __init__(self, xmlArgument):
        """
        
        """
        
        self.type = None
        self.frame = None
        self.value = None
        
        if xmlArgument is None:
            return
        self.type = xmlArgument.attrib['type']
        if self.type == 'var':
            self.frame, self.value = str.split(xmlArgument.text, "@")
        else:
            self.value = xmlArgument.text

    def __str__(self):
        return f'{self.type}: {"" if self.frame is None else self.frame}{"" if self.value is None else self.value}'