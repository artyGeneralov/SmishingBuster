import pandas as pd

class ExcelHelper:


    DEFAULT_ENCODING = "ISO-8859-1"

    def __init__(self, filename, encoding=None):
        self.filename = filename
        self.encoding = encoding if encoding is not None else ExcelHelper.DEFAULT_ENCODING
        if filename.endswith('.xlsx'):
            self.filedata = pd.read_excel(self.filename)
        else:
            self.filedata = pd.read_csv(self.filename, encoding=self.encoding)

    def getColumnAsList(self, attributeName):
        return self.filedata[attributeName].tolist()
    
    def getColumnAsListByNumber(self, columnNumber):
        return self.filedata.iloc[:, columnNumber].tolist()

    def getAllAttributes(self):
        return {col:self.filedata[col].tolist() for col in self.filedata.columns}
        

