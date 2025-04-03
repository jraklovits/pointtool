import pandas as pd
from struct import unpack, pack
import io
import os


class CRDREADER:
    def __init__(self, fileData):
        self.file_like = io.BytesIO(fileData)
        self.get_format()


    
    def get_format(self):
        try:
            self.file_like.seek(86)
            header_byte = self.file_like.read(1)
            if header_byte:
                self.format = int(header_byte.decode("utf-8"))
            else:
                self.format = 1
            
            self.header_seek = 104 if self.format == 2 else 0

        except (OSError, ValueError, UnicodeDecodeError) as e:
            self.header_seek = 0
            self.format = 1 

    def read_crd(self):
        data = []

        record_format = "ddd32s" 
        buf_len = 56  

        if self.format == 2:
            record_format = "ddd32s10s"
            buf_len = 66
        
        self.file_like.seek(self.header_seek)
        
        counter = 1
        while True:
            record = self.file_like.read(buf_len)
            if not record:
                break  # Stop at EOF

            if len(record) != buf_len:
                print(f"Warning: Incomplete record found ({len(record)} bytes), skipping...")
                continue 

            unpacked = unpack(record_format, record)
            
            if self.format == 2:
                ## Get Point Name which is the _
                northing, easting, elevation, description, name = unpacked
                description = str(description)[2:-1].replace("\\x00", "")
                name = str(name)[2:-1].replace("\\x00", "")
                data.append((northing, easting, elevation, description, name))

            else:
                ## Get Point Number by offset in the file.
                northing, easting, elevation, description = unpacked
                description = str(description)[2:-1].replace("\\x00", "")
                data.append((northing, easting, elevation, description, counter))
            counter = counter + 1

        # Create DataFrame
        df = pd.DataFrame(data, columns=["North", "East", "Height", "Description", "Name"])
        df = df[["Name", "North", "East", "Height", "Description"]]

        if self.format == 1:
            df = df.drop(0)
            df = df[df['North'] != 0]

        self.df = df
        return df