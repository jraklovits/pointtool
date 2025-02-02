####Build a Class to get info out of mxl file
###Should return a data frame object with
###POINT,NORTHING,EASTING,ELEVATION,DESCRIPTION,LAYER,DATE,TYPE

import pandas as pd
import re
import xml.etree.cElementTree as et
from os import path
from pathlib import Path
import sqlite3 as sql
import os

nameSearch  = '{tps}ProjectInfo/{tps}Name'
codeSearch = '{tps}CodeDescriptions/{tps}CodeDescription'
layerSearch = '{tps}Layers/{tps}Layer'

class MXL:
    def __init__(self, filename):
        tree = et.parse(filename)
        self.root = tree.getroot()


    def getCodes(self):
        codes = {}
        for table in self.root.findall(codeSearch):
            codeNum = table.attrib['id']
            for i in table.findall('{tps}Name'):
                codeName = i.text
            codes[codeNum]=codeName
        return codes
    def getCodesdf(self):
        codes = {}
        for table in self.root.findall(codeSearch):
            codeNum = table.attrib['id']
            for i in table.findall('{tps}Name'):
                codeName = i.text
            codes[codeNum]=codeName
        dfcodes = pd.DataFrame.from_dict(codes)

    def getLayers(self):
    # use this!
        layers = {}
        for table in self.root.findall(layerSearch):
            layerNum = table.attrib['id']
            for i in table.findall('{tps}Name'):
                layerName = i.text
            layers[layerNum]=layerName
        return layers

    def getLayersdf(self):
    # use this!
        layers = {}
        for table in self.root.findall(layerSearch):
            layerNum = table.attrib['id']
            for i in table.findall('{tps}Name'):
                layerName = i.text
            layers[layerNum]=layerName
        dflayers = pd.DataFrame.from_dict(layers, orient='index')
        return dflayers
    
    
    def getPoints(self):  
        codeLib = self.getCodes()
        layerLib = self.getLayers()
        pntNames = []
        layers = []
        timeStamps = []
        layers = []
        codes = []
        codeStrings = []
        notes = []
        Ns = []
        Es = []
        Zs = []
        root1 =  self.root.find("{tps}PlanEntities")
        for i in root1.iter('{tps}DesignPoint'):
            #pnt ID
            pntname = i.attrib['id']
            #pnt ID
            #pntName
            for j in i.iter('{tps}Name'):
                name = j.text
            #pntname
            #Layers
            for j in i.iter('{tps}Layer'):
                layer = j.attrib['idRef']
            #Layers
            #Notes
            note = i.find('{tps}Station/{tps}Notes')
            if note is None:
                note = ""
            else:
                note = note.text
                note = note.replace('"', "")
                note = note.replace("'", "") 
            #Notes
            #TimeStamps
            j = i.find('{tps}Station/{tps}TimeStamp')
            if j is None:
                timestamp = '1900-01-01T12:00:00Z'
            else:
                timestamp = j.text
            ###Need to conform to date only
            timestamp = timestamp.split('T')[0]
            #TimeStamps
            #Code  There can be more than one
            r = i.iter('{tps}CodeString')
            m = [*r]
            if len(m) >=1:
                codestr = m[0].text
                codestr = codestr.replace('"', "")
                codestr = codestr.replace("'", "") 
                #
            else:
                codestr = ""
            r = i.iter('{tps}CodeDescription')
            m = [*r]
            code = ""
            if len(m) == 2:
                #This catches multi-codes
                code2 = m[1].attrib['idRef']
            else:
                code2 = ""
            if len(m) > 2:
                #This Catches more than 2
                for j in range(2, len(m)):
                    failure = "Failure: " + name + " " +m[j].attrib['idRef']
                    #eg.msgbox(failure)
            try:
                code = m[0].attrib['idRef']
                code = code.replace('"', "")
                code = code.replace("'", "") 
            except:
                pass
            #code
            #NEZ
            for j in i.iter('{tps}Position'):
                neh = j.iter('{tps}NEH')
                nehlist = [*neh]
                if len(nehlist) == 1:
                    for k in j.iter('{tps}North'):
                        n=round(float(k.text), 3)
                    for k in j.iter('{tps}East'):
                        e=round(float(k.text), 3)
                    for k in j.iter('{tps}Height'):
                        z=round(float(k.text), 3)
            #NEZ
            #Check for durability
            if code2 and code != code2:
                pntNames.append(name+'_')
                Ns.append(n)
                Es.append(e)
                Zs.append(z)
                #codes.append(codeLib[code2])
                codes.append(codeLib[code]+"-" + codestr +'*' + note)
                #codeStrings.append("")
                layers.append(layerLib[layer])
                #notes.append(note)
                timeStamps.append(timestamp)
            if all([pntname, n, layer, timestamp]) == True:
                pntNames.append(name)
                Ns.append(n)
                Es.append(e)
                Zs.append(z)
                try:
                    #codes.append(codeLib[code2])
                    if codestr == "":
                        if note =="":
                            codes.append(codeLib[code])
                        else:
                            codes.append(codeLib[code]+ '*' + note)
                    else:
                        if note =="":
                            codes.append(codeLib[code] + '-'+ codestr)
                        else:
                            codes.append(codeLib[code]+ "-"+ codestr +'*'+note)
                    #codeStrings.append(codestr)
                except:
                    codes.append("")
                    #codeStrings.append(codestr)
                layers.append(layerLib[layer])
                #notes.append(note)
                timeStamps.append(timestamp)
            else:
                pass
        #datadict =  {"Point": pntNames, "Northing":Ns, "Easting":Es, "Elevation":Zs, "Description":codes, "Code Strings" : codeStrings, "Notes" : notes, "Layer":layers,  "Date":timeStamps}
        datadict =  {"Point": pntNames, "Northing":Ns, "Easting":Es, "Elevation":Zs, "Description":codes, "Layer":layers,  "Date":timeStamps}
        df = pd.DataFrame.from_dict(datadict)
        return df
