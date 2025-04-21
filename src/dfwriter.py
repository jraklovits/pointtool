from venv import create
import pandas as pd
import zipfile
import io
import base64
from struct import pack
import os

class DFWRITER:
    def __init__(self, df):
        self.df = df


    def createCrds(self, chunk, format=2):
        # Rename columns to standard names
        rename_map = {
            'Point': 'Name',
            'Northing': 'North',
            'Easting': 'East',
            'Elevation': 'Height'
        }
        chunk = chunk.rename(columns=rename_map)

        # Convert to numeric where appropriate
        for col in ['North', 'East', 'Height']:
            chunk[col] = pd.to_numeric(chunk[col], errors='coerce')

        output = io.BytesIO()

        if format == 2:
            # ---- Alphanumeric Header ----
            header_id = 0
            header_date = "04/20/2025".ljust(32, '\x00').encode('utf-8')  # Date format adjusted
            header_desc = "TEST".ljust(32, '\x00').encode('utf-8')
            header_format = "New CRD Format2".ljust(32, '\x00').encode('utf-8')

            # Packing data into the binary format
            header = pack('d32s32s32s', header_id, header_date, header_desc, header_format)
            output.write(header)

            # Write records sequentially
            for _, row in chunk.iterrows():
                northing = float(row['North'])
                easting = float(row['East'])
                elevation = float(row['Height'])
                description = str(row['Description'])[:32].ljust(32, '\x00').encode('utf-8')
                name = str(row['Name'])[:10].ljust(10, '\x00').encode('utf-8')

                record = pack('ddd32s10s', northing, easting, elevation, description, name)
                output.write(record)

        elif format == 1:
            # ---- Numeric Header ----
            max_pt = int(chunk['Name'].astype(int).max())
            job_number = 1001.0  # or use input value
            job_desc = "Numeric CRD File".ljust(32, '\x00').encode('utf-8')
            header = pack('ddd32s', float(max_pt), job_number, 0.0, job_desc)
            output.write(header)

            # Pre-fill remaining space
            total_size = (max_pt + 1) * 56
            output.write(b'\x00' * (total_size - 56))  # We already wrote 56 bytes

            # Write each point at its offset
            for _, row in chunk.iterrows():
                pt_num = int(row['Name'])
                northing = float(row['North'])
                easting = float(row['East'])
                elevation = float(row['Height'])
                description = str(row['Description'])[:32].ljust(32, '\x00').encode('utf-8')

                record = pack('ddd32s', northing, easting, elevation, description)
                output.seek(pt_num * 56)
                output.write(record)

        output.seek(0)
        return output
   
    def createFldTxt(self):
        #Creates Folders for layers, then outputs a text file for each date named LAYER - DATE
        zip_buf = io.BytesIO()
        self.df['Date'] = pd.to_datetime(self.df['Date']).dt.strftime('%m-%d-%y')
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:    
            for (layer, date), group in self.df.groupby(['Layer', 'Date']):
                group = group.drop(['Layer','Date'], axis=1)
                group.reset_index()
                with zf.open(f'{layer} {date}.txt', "w") as x:
                      group.to_csv(x,index=False,header=False)
        zip_buf.seek(0)
        b64 = base64.b64encode(zip_buf.read()).decode()
        del zip_buf
        return b64

    def createFldCrd(self, format=2):
        #Creates Folders for layers, then outputs a text file for each date named LAYER - DATE

        zip_buf = io.BytesIO()
        self.df['Date'] = pd.to_datetime(self.df['Date']).dt.strftime('%m-%d-%y')
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:    
            for (layer, date), group in self.df.groupby(['Layer', 'Date']):
                group = group.drop(['Layer','Date'], axis=1)
                group.reset_index()
                with zf.open(f'{layer} {date}.crd', "w") as buffer:
                     # group.to_csv(buffer,index=False,header=False)
                     buffer.write(self.createCrds(group).getvalue())
        zip_buf.seek(0)
        b64 = base64.b64encode(zip_buf.read()).decode()
        del zip_buf
        return b64
            

    def createTXTNoDates(self):
        ##Creates Folders for layers, then outputs a text file for each layer
        zip_buf = io.BytesIO()
        workingDF = self.df.drop('Date', axis=1)
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            groups = workingDF.groupby('Layer')
            for layers, group in groups:
                group = group.drop(['Layer'], axis=1)
                with zf.open(f'{layers}.txt',"w") as buffer:
                    group.to_csv(buffer,index=False,header=False)
        zip_buf.seek(0)
        b64 = base64.b64encode(zip_buf.read()).decode()
        del zip_buf
        return b64
    
    def createCrdNoDates(self, format=2):
        # Creates Folders for layers, then outputs a CRD file for each layer
        zip_buf = io.BytesIO()
        workingDF = self.df.drop('Date', axis=1)

        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            groups = workingDF.groupby('Layer')
            
            for layer, group in groups:
                group = group.drop(['Layer'], axis=1)
                with zf.open(f'{layer}.crd', "w") as buffer:
                    buffer.write(self.createCrds(group, format).getvalue())
        
        zip_buf.seek(0)
        b64 = base64.b64encode(zip_buf.read()).decode()
        del zip_buf

        return b64




    

