import pandas as pd
import zipfile
import io
import base64


import os


class DFWRITER:
    def __init__(self, df):
        self.df = df

    # def __init__(self, df, destdir):
    #     self.df = df
    #     self.destdir = destdir

    # def layerFolder(self, filePath):
    #     filePath = filePath.strip()
    #     try:
    #         os.makedirs(filePath)
    #     except FileExistsError:
    #         pass
    
    def createFldTxt(self):
        zip_buf = io.BytesIO()
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
            ##group.to_csv(f'{layer} {date}.txt', index=False, header=False)
            # self.layerFolder(os.path.join(self.destdir,f'{layer}'))
            # group.to_csv(os.path.join(self.destdir,f'{layer}',f'{layer} {date}.txt'), index=False, header=False)
            

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
    
    def createTXT(self):
        try:
            self.df = self.df.drop('Date', axis=1)
            self.df = self.df.drop('Layer', axis=1)
        except:
            pass
        self.df.to_csv(filesaveas + '.txt', index=False, header=False)

    

