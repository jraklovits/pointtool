import flet as ft


def df2tbl(df):
    return  ft.DataTable(
        columns=[ft.DataColumn(ft.Text(header)) for header in df.columns],
        rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(row[header]))) for header in df.columns])
        for _, row in df.iterrows()
        ]
    )

def df2lv(df):
        lv = ft.ListView(expand=1, spacing=5, auto_scroll=True)
        dt = ft.DataTable(
        columns=[ft.DataColumn(ft.Text(header)) for header in df.columns],
        rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(row[header]))) for header in df.columns])
        for _, row in df.iterrows()
            ],column_spacing=10
        )
        lv.controls.append(dt)
        return lv


