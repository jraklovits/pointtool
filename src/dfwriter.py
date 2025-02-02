import pandas as pd
import os


class DFWRITER:
    def __init__(self, df, destdir):
        self.df = df
        self.destdir = destdir
        print(self.df)
        print(self.destdir)

    def layerFolder(self, filePath):
        filePath = filePath.strip()
        try:
            os.makedirs(filePath)
        except FileExistsError:
            pass
    
    def createFldTxt(self):
        #Creates Folders for layers, then outputs a text file for each date named LAYER - DATE
        self.df['Date'] = pd.to_datetime(self.df['Date']).dt.strftime('%m-%d-%y')
        for (layer, date), group in self.df.groupby(['Layer', 'Date']):
            group = group.drop(['Layer','Date'], axis=1)
            group.reset_index()
            ##group.to_csv(f'{layer} {date}.txt', index=False, header=False)
            self.layerFolder(os.path.join(self.destdir,f'{layer}'))
            group.to_csv(os.path.join(self.destdir,f'{layer}',f'{layer} {date}.txt'), index=False, header=False)

    def createTXTNoDates(self):
        ##Creates Folders for layers, then outputs a text file for each layer
        self.df = self.df.drop('Date', axis=1)
        groups = self.df.groupby('Layer')
        for layers, group in groups:
            group = group.drop(['Layer'], axis=1)
            group.to_csv(os.path.join(self.destdir,f'{layers}.txt'),index=False,header=False)

    def createTXT(self,filesaveas):
        self.df = self.df.drop('Date', axis=1)
        self.df = self.df.drop('Layer', axis=1)
        self.df.to_csv(filesaveas, index=False, header=False)

    

