import flet as ft # type: ignore
import os.path
import mxlreader as mxl
import txtreader as txt
import sqlitereader as sql
import crdreader as crd
import dfwriter as dfw
import pandas as pd # type: ignore
import tableviewer as tv


filetype = 'mxl'
saveloc = ''
savehelp = 'Saving will create folders for layers, and a text file for each day and layer inside.'
global dataframe

def get_file_type(x):
    '''RETURN STRING FILE EXTENSION'''
    extension = os.path.splitext(x)[1]
    return extension

def mxl2df(filepath):
    print('mxl')
    t = mxl.MXL(filepath)
    x = t.getPoints()
    y = t.getLayersdf()
    return x,y

def txt2df(filepath):
    print('txt')
    t = txt.TXT(filepath)
    x = t.getPoints()
    y = t.getLayers()
    return x,y

def sql2df(filepath):
    print('sql')
    t = sql.SQL(filepath)
    x =  t.getPntsCodesLayers()
    y = t.getLayers()
    t.close()
    return x,y

def df2csv(df, destpath):
    t = dfw.DFWRITER(df,destpath)
    t.createFldTxt()

def crd2df(filepath):
    t = crd.CRDREADER(filepath)
    t.read_crd()
    return t.df

def main(page: ft.Page):

    #######UTILITY###############
    def getpnts(ft):
        match ft:
            case ".mxl":
                x = mxl2df(selected_files_0.value)[0]
                page.add(layerdate)
                page.add(layeronly)
                page.add(pointonly)
                page.add(selected_files_1)
                filesel.update()
                selected_files_1.update()
                count_row = x.shape[0]
                layerlook.visible =True
                layerlook.update()
            case ".txt":
                try:
                    x = txt2df(selected_files_0.value)[0]
                    page.add(layerdate)
                    page.add(layeronly)
                    #page.add(layer_only_path)
                    page.add(pointonly)
                    page.add(selected_files_1)
                    #page.add(point_only_path)
                    filesel.update()
                    selected_files_1.update()
                    count_row = x.shape[0]
                    layerlook.visible =True
                    layerlook.update()
                except:
                    print("yikes")
            case ".mjf":
                x = sql2df(selected_files_0.value)[0]
                count_row = x.shape[0]
                layerlook.visible =True
                layerlook.update()
            case ".bak":
                x = sql2df(selected_files_0.value)[0]
                count_row = x.shape[0]
                layerlook.visible =True
                layerlook.update()
            case ".crd":
                x = crd2df(selected_files_0.value)
               #page.add(selected_files_1)
                #selected_files_1.update()
                page.add(pointonly)
                page.add(point_only_path)
                count_row = x.shape[0]
        global dataframe
        dataframe = x
        pointcount.value =str(count_row) + ' Points in the file'
        pointcount.update()
        page.add(tv.df2lv(x))
        selected_files_1.value = savehelp
        filesel.visible = False
        filesel.update()


    def show_layers(e):
        filetype = get_file_type(selected_files_0.value)
        if filetype =='.mjf':
            layers = (sql2df(selected_files_0.value))[1]
            layers = layers.drop('keyLayers', axis=1)
        if filetype == '.mxl':
            layers = (mxl2df(selected_files_0.value))[1]
            # layersdict =(mxl2df(selected_files_0.value))[1]
            # layers = pd.DataFrame.from_dict(layersdict,orient='index', columns=['Name'])
        if filetype =='.txt':
            layers = (txt2df(selected_files_0.value))[1]
        if filetype =='.bak':
            layers = (sql2df(selected_files_0.value))[1]
            layers = layers.drop('keyLayers', axis=1)
        page.add(ft.Divider(height=1, color="white"))
        page.add(tv.df2lv(layers))
        layerlook.visible=False
        page.update()
    #######UTILITY###############


    # File picker handlers and setup
    ##############FILE SELECT############
    def pick_files_result_0(e: ft.FilePickerResultEvent):
        global dataframe
        selected_files_0.value = e.files[0].path
        selected_files_0.update()
        ft = get_file_type(selected_files_0.value)
        print(ft)
        #filetype = ft
        getpnts(ft)

    pick_files_dialog_0 = ft.FilePicker(
        on_result=pick_files_result_0
    )
    selected_files_0 = ft.Text("No file chosen", size=14)

    page.overlay.append(pick_files_dialog_0)
    ##############FILE SELECT############

    ##############FILE SAVE############
    def pick_files_result_1(e: ft.FilePickerResultEvent):
        selected_files_1.value = e.path
        saveloc = selected_files_1.value
        selected_files_1.update()
        x = dfw.DFWRITER(dataframe, saveloc)
        x.createFldTxt()
        show_alert_dialog_0()
        layerdate.disabled = True
        layerdate.update()
    def pick_files_result_2(e: ft.FilePickerResultEvent):
        selected_files_1.value = e.path
        saveloc = selected_files_1.value
        selected_files_1.update()
        x = dfw.DFWRITER(dataframe, saveloc)
        #x.createFldTxt()
        x.createTXTNoDates()
        show_alert_dialog_0()
        layerdate.disabled = True
        layerdate.update()
    def pick_files_result_3(e: ft.FilePickerResultEvent):
        selected_files_1.value = e.path
        saveloc = selected_files_1.value
        #selected_files_1.update()
        
        # point_only_path.value = e.path
        # saveloc = point_only_path.value
        # point_only_path.update()
        x = dfw.DFWRITER(dataframe, saveloc)
        #x.createFldTxt()
        x.createTXT(saveloc)
        show_alert_dialog_0()
        # layerdate.disabled = True
        # layerdate.update()

    layerdate_dialog = ft.FilePicker(
        on_result=pick_files_result_1
    )
    selected_files_1 = ft.Text("No file chosen", size=14)

    layer_dialog = ft.FilePicker(
        on_result=pick_files_result_2
    )
    layer_only_path = ft.Text("No file chosen", size=14)

    point_dialog = ft.FilePicker(
        on_result=pick_files_result_3
    )
    point_only_path = ft.Text("No file chosen", size=14)

    page.overlay.append(layerdate_dialog)
    page.overlay.append(point_dialog)
    page.overlay.append(layer_dialog)
    ##############FILE SAVE############


    # Alert dialog handlers and setup
    def show_alert_dialog_0():
        page.open(alert_dialog_0)
        page.update()
    def toggle_alert_dialog_0():
        if alert_dialog_0.open: 
            page.close(alert_dialog_0)
        else:
            page.open(alert_dialog_0)
        page.update()

    alert_dialog_0 = ft.AlertDialog(
        modal=False,
        title=ft.Text("Files Saved"),
        content=ft.Text("Success!"),
        actions=[ft.TextButton("OK", on_click=lambda _: (page.close(alert_dialog_0), page.update()))]
    )
    page.overlay.append(alert_dialog_0)

    # Button function definitions
    filesel = ft.ElevatedButton(
            text="Choose File...",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: pick_files_dialog_0.pick_files(allow_multiple=False, allowed_extensions=["mxl", "csv", "txt", "mjf", "bak","crd"])
    )
    layerlook = ft.ElevatedButton(
            text="Show Layers",
            visible=False,
            on_click=show_layers
    )

    layerdate = ft.ElevatedButton(
            text="Save Folders of Layers and Each Text File by Date (ie AB-STORM 05-05-22)",
            icon=ft.icons.SAVE_AS,
            on_click=lambda _: layerdate_dialog.get_directory_path()
    )
    layeronly = ft.ElevatedButton(
            text="Save One Text File for Each Layer (ie AB-STORM)",
            icon=ft.icons.SAVE_AS,
            on_click=lambda _: layer_dialog.get_directory_path()
    )
    pointonly = ft.ElevatedButton(
            text="Save Everything in One Text File",
            icon=ft.icons.SAVE_AS,
            on_click=lambda _: point_dialog.save_file(allowed_extensions=['txt'])
    )
    
    pointcount = ft.Text(value='Select a file')
    page.add(pointcount)
    page.add(filesel,selected_files_0)
    page.add(layerlook)
    page.window.width= 1600

ft.app(main)