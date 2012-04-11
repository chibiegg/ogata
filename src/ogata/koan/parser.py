# encoding=utf-8
import csv
import StringIO

class RishuParser(object):
    """履修情報のテキストファイルをパースする"""
    
    rishu = {} #月曜日1限は "1-1"
    
    def __init__(self,text,encoding="sjis_2004"):
        self.text = text
        self.encoding = encoding
        self.parse()
    
    def parse(self):
        """パースする"""
        
        #CSVを二次元配列に
        rows = []
        csvfile = StringIO.StringIO(self.text)
        for row in csv.reader(csvfile):
            rows.append(row)
        
        #セメスター情報
        
        
        #時間割
        for youbi in range(1,7):
            for zigen in range(1,8):
                col = youbi
                row = 1+4*zigen
                self.rishu["%d-%d" % (youbi,zigen)] = None
                code = rows[row][col].decode(self.encoding)
                if code!=u"未登録":
                    name = rows[row+1][col].decode(self.encoding)
                    teacher = rows[row+2][col].decode(self.encoding)
                    place = rows[row+3][col].decode(self.encoding)
                    print name
                    self.rishu["%d-%d" % (youbi,zigen)] = {
                                                           "code":code,"name":name,"teacher":teacher,"place":place
                                                           }
        print self.rishu