import os
import pandas as pd
from io import StringIO

class TXT:
    def __init__(self, filename):
        #self.df = pd.read_csv(filename,index_col=False, dtype=  str,names=['Points','Northings','Eastings','Elevations','Descriptions','Layers','Dates'],parse_dates=['Dates'])
        if isinstance(filename, str):
            self.df = pd.read_csv(StringIO(filename),index_col=False, dtype=  str,names=['Point','Northing','Easting','Elevation','Description','Layer','Date'])
        else:
            self.df = pd.read_csv(filename,index_col=False, dtype=  str,names=['Point','Northing','Easting','Elevation','Description','Layer','Date'])
    def getLayers(self):
        self.df['Layer'] =  self.df['Layer'].str.strip().replace(" ","_")
        self.df = self.df.drop('Point', axis=1)
        self.df = self.df.drop('Northing', axis=1)
        self.df = self.df.drop('Easting', axis=1)
        self.df = self.df.drop('Elevation', axis=1)
        self.df = self.df.drop('Description', axis=1)
        self.df = self.df.drop('Date', axis=1)
        self.df = self.df.drop_duplicates()
        return self.df
    
    def getPoints(self):
        self.df = self.df.fillna('z')
        self.df['Layer'] =  self.df['Layer'].str.strip().replace(" ","_")
        #layer remover
        # if layersToKeep != []:
        #     df = df[df['Layer'].isin(layersToKeep)]
        # 
        #descriptors
        self.df['Description'] =  self.df['Description'].str.strip()
        self.df['Description'] = self.df['Description'].str.replace(" ","_")
        self.df['Description'] = self.df['Description'].str.replace("'","")
        self.df['Description'] = self.df['Description'].str.replace('"',"")
        self.df['Description'] = self.df['Description'].str.replace("`","")
        #print(self.df['Dates'])
        # if df['Dates'] < 0:
        #     df['Dates'] = 0
        
        #self.df['Dates'] = pd.to_datetime(self.df['Dates']).dt.strftime('%m-%d-%y')
        return self.df