import pandas as pd
import zipfile
import io
import base64
from struct import pack
import os

class DFWRITER:
    def __init__(self, df):
        self.df = df
    
    def createFldTxt(self):
        zip_buf = io.BytesIO()
        print(self.df)
        #Creates Folders for layers, then outputs a text file for each date named LAYER - DATE
        self.df['Date'] = pd.to_datetime(self.df['Date']).dt.strftime('%m-%d-%y')
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:    
            for (layer, date), group in self.df.groupby(['Layer', 'Date']):
                group = group.drop(['Layer','Date'], axis=1)
                group.reset_index()
                with zf.open(f'{layer} {date}.txt', "w") as buffer:
                      group.to_csv(buffer,index=False,header=False)
        zip_buf.seek(0)
        b64 = base64.b64encode(zip_buf.read()).decode()
        del zip_buf
        return b64

    def createFldCrd(self, format=2):
        zip_buf = io.BytesIO()
        print (self.df)
        #Creates Folders for layers, then outputs a text file for each date named LAYER - DATE
        #self.df['Date'] = pd.to_datetime(self.df['Date']).dt.strftime('%m-%d-%y')
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:    
            for (layer, date), group in self.df.groupby(['Layer', 'Date']):
                group = group.drop(['Layer','Date'], axis=1)
                group.reset_index()
                with zf.open(f'{layer} {date}.txt', "w") as buffer:
                    required_cols = ['Name', 'North', 'East', 'Height', 'Description']
                    if not all(col in group for col in required_cols):
                        # Rename columns if they exist with different names
                        rename_map = {
                            'Point': 'Name',
                            'Northing': 'North',
                            'Easting': 'East',
                            'Elevation': 'Height'
                        }
                        self.df = self.df.rename(columns=rename_map)
                             # Ensure required columns exist
                        required_cols = ['Name', 'North', 'East', 'Height', 'Description']
                        if not all(col in self.df.columns for col in required_cols):
                            # Rename columns if they exist with different names
                            rename_map = {
                                'Point': 'Name',
                                'Northing': 'North',
                                'Easting': 'East',
                                'Elevation': 'Height'
                            }
                            self.df = self.df.rename(columns=rename_map)
                        
                        # Convert numeric columns
                    for col in ['North', 'East', 'Height']:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    # Create CRD file
                    output = io.BytesIO()
                    
                    # Write header for format 2
                    if format == 2:
                        output.write(b'\x00' * 86)
                        output.write(b'2')
                        output.write(b'\x00' * 17)
            
                    # Write records
                    for _, row in self.df.iterrows():
                        northing = float(row['North'])
                        easting = float(row['East'])
                        elevation = float(row['Height'])
                        description = str(row['Description'])[:32].ljust(32, '\x00').encode('utf-8')
                        if format == 2:
                            name = str(row['Name'])[:10].ljust(10, '\x00').encode('utf-8')
                            record = pack('ddd32s10s', northing, easting, elevation, description, name)
                        else:
                            record = pack('ddd32s', northing, easting, elevation, description)    
                        output.write(record)
                    output.seek(0)
                    zip_buf.write(output.read())
                      #group.to_csv(buffer,index=False,header=False)
        b64 = base64.b64encode(zip_buf.read()).decode() 
        del zip_buf
        return b64
            

    def createTXTNoDates(self):
        ##Creates Folders for layers, then outputs a text file for each layer
        zip_buf = io.BytesIO()
        self.df = self.df.drop('Date', axis=1)
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            groups = self.df.groupby('Layer')
            for layers, group in groups:
                group = group.drop(['Layer'], axis=1)
                with zf.open(f'{layers}.txt',"w") as buffer:
                    group.to_csv(buffer,index=False,header=False)
        zip_buf.seek(0)
        b64 = base64.b64encode(zip_buf.read()).decode()
        del zip_buf
        return b64
    




    

