import sqlite3
import pandas as pd
import datetime as dt
import numpy as np
from io import StringIO


##GET RID OF HIDDEN CODES - WACKY CODES


#table names
POINT_TABLE = 'tblStations'
OTHER_POINTS = 'tblSoPoints'
CODE_TABLE = 'tblCodeDefs'
CODE_TABLE_DEF = 'tblCodesToPts'
LAYER_TABLE = 'tblLayers'
LOC_TABLE = 'tblCrdCalibrations'
CODES_TO_REMOVE = ['{|HiddenCode|}']

#Columns that are not needed
no_good_codes = ['LineColor','LineStyleIndex','LineWidth','MarkColor', 'CodeType','AttribPrompt','MarkStyleIndex',
                 'FillColor','FillStyle','Transparency', 'DtmFlags','fkeyUserSymbol', 'fkeyCtrlCode1', 'fkeyCtrlCode2', 'keyCodeDef',
                 'fkeyPoint', 'fkeyCodeDef', ]
no_good_layers = ['Color', 'LineStyleIndex', 'LineWidth', 'MarkStyleIndex', 'IsSwitchedOff','Description',
                   'OrderingNumber', 'FillColor','Transparency', 'IsLocked', 'fkeyCodeDefs', 'FillStyle' ]
no_good_points = ['fkeySoPoint', 'fkeyDataset','DeletedFlag','TimeSystem', 'UseInWAH', 
                    'UseInWAV', 'WaSwitchEnabled','fkeyCorrectBaseKP']
no_good_final = ['keyStation', 'keyCodesToPoints', 'fkeyLayer', 'DescName', 'keyLayers']

strdeleter = ['{|HiddenCode|}']



class SQL:
    def __init__(self, filename):
        #UGH
        self.conn = sqlite3.connect(":memory:")
        self.conn.deserialize(filename)

    def getTables(self):
        #get all tables in database
        df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", self.conn)
        return df['name'].to_list()
    
    def getPoints(self):
        #get all points in database
        df = pd.read_sql_query("SELECT * FROM "+ POINT_TABLE, self.conn)
        df = df.drop(no_good_points,axis=1)
        return df

    def getOtherPoints(self):
        #get all points in database
        df = pd.read_sql_query("SELECT * FROM "+ OTHER_POINTS, self.conn)
       # df = df.drop(no_good_points,axis=1)
        return df
    
    def getCodes(self):
        #get all codes in database
        df = pd.read_sql_query("SELECT * FROM "+ CODE_TABLE, self.conn)
        df2 = pd.read_sql_query("SELECT * FROM "+ CODE_TABLE_DEF, self.conn)
        df = pd.merge(df2,df, left_on='fkeyCodeDef', right_on='keyCodeDef', how='left')
        df = df.drop(no_good_codes,axis=1)
        return df
    
    def getLayers(self):
        #get all layers in database
        df = pd.read_sql_query("SELECT * FROM "+ LAYER_TABLE, self.conn)
        df = df.drop(no_good_layers,axis=1)
        return df
    
    def getResects(self):
        table_name = 'tblTsOccups'
        df = pd.read_sql_query("SELECT * FROM "+ table_name, self.conn)
        return df
    
    def getLoc(self):
        df = pd.read_sql_query("SELECT * FROM "+ LOC_TABLE, self.conn)
        return df

    
    def getPointsAll(self):
        out = [self.getCodes(),self.getLayers(), self.getPoints()]
        return out
    
    def makePretty(self):
        ptdf = self.getPoints()
        codedf = self.getCodes()
        layerdf = self.getLayers()

    def getRando(self, table_name):
        df = pd.read_sql_query("SELECT * FROM "+ table_name, self.conn)
        return df

    def csvAllTables(self):
        for table in self.getTables():
            df = self.getRando(table)
            df.to_csv(table + '.csv')
    
    def csvTable(self, df, name):
        try:
            df.to_csv(name + '.csv' , index=False)
        except:
            pass
    
    def getPntsCodesLayers(self):
        pts = self.getPoints()
        #pts = self.getOtherPoints()
        codes = self.getCodes()
        layers = self.getLayers()
        pts = pd.merge(pts,codes,left_on= 'keyStation', right_on='keyCodesToPoints',how='left' )
        pts = pd.merge(pts,layers,left_on= 'fkeyLayer', right_on='keyLayers',how='left' )
        pts = pts.drop(no_good_final,axis=1)
        #COLUMN RENAME
        pts = pts.rename(columns={'Name_x': 'Point', 'C1': 'Northing', 'C2' : 'Easting', 'C3' : 'Elevation','SecondsFrom1970': 'Date', 'nameCode' : 'Code', 'Name_y' : 'Layer', 'Notes': 'Note' })
        #GET RID OF PLAN POINTS
        pts =pts[pts.StationType != 18]
        pts['Code'] = pts['Code'].astype(str)
        #pts = pts[~pts['Code'].isin(strdeleter)]
       # pts = pts[~pts.Code.str.contains('{|HiddenCode|}')]
        #pts = pts[pts.Code != '{|HiddenCode|}']
        #pts = pts[~pts['Code'].isin([CODES_TO_REMOVE])]
        #pts['Description'] = pts[['Code','CodeString','Note']].agg('-'.join, axis=1)
        pts['Description'] = pts['Code'].astype(str)+ ('-')+ pts['CodeString'].astype(str) + '*' + pts['Note']
        #pts['Description'] = pd.concat(pts['Description'], pts['Notes'])
        #REORDER
        pts =pts[['Point','Northing', 'Easting','Elevation','Description','Layer', 'Date']]
        #Clean up date info
        pts['Date'] = pd.to_datetime(pts['Date'], unit='s')
        pts['Date'] = pts['Date'].dt.strftime('%m-%d-%Y')
        pts = pts.replace('',np.nan).fillna(" ")
        return pts



    def close(self):
        self.conn.close()
   


