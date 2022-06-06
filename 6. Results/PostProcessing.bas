Attribute VB_Name = "PostProcessing"
'Let's try IBC - IBCF
'First create a function that creates the pivot table, then a wrapper

Public YrList As Variant

'Have public the list of sheets and product names
Public SheetList As Variant
Public ProdList As Variant

'Later I will have a format subroutine that formats everything


Sub CreatePivot1(SourceSheet As String)

    YrList = Array(2022, 2023)

    'DESCRIPTION: Create the Pivot Table of Type 1
    'INPUT: SourceSheet - Name of the sheet where the source data comes from
    
    'Assuming the correct sheet is selected, create Pivot Table with
    ' - Factory in Rows
    ' - Years in Values
    ' - Product in Filter
    ' - Show Report Filter Pages
    
    '0. Get the Coordinates of the Source Data
    Worksheets(SourceSheet).Select
    Range("A1").End(xlDown).End(xlToRight).Select
    EndPoint = "R" & CStr(ActiveCell.Row) & "C" & CStr(ActiveCell.Column)
    
    PTName = "Pivot"
    
    '1. Insert Pivot Table
    Range("A1").Select
    Sheets.Add Before:=Worksheets(SourceSheet)
    ActiveSheet.Name = PTName
    Sheets(PTName).Select
    ActiveWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:= _
        SourceSheet & "!R1C1:" & EndPoint, Version:=8).CreatePivotTable _
        TableDestination:=PTName & "!R3C1", TableName:=PTName, DefaultVersion _
        :=8
    Cells(3, 1).Select
    With ActiveSheet.PivotTables(PTName)
        .ColumnGrand = False
        .RowGrand = False
    End With
    ActiveSheet.PivotTables(PTName).RepeatAllLabels 2
    
    '2. Put Factory in Rows
    With ActiveSheet.PivotTables(PTName).PivotFields("Factory")
        .Orientation = xlRowField
        .Position = 1
    End With
    
    '3. Put Years in Value
    For Yr = YrList(0) To YrList(1)
        ActiveSheet.PivotTables(PTName).AddDataField ActiveSheet.PivotTables( _
        PTName).PivotFields(CStr(Yr)), "Sum of " & Yr, xlSum
    Next Yr
    
    '4. Put Product into Filters
    With ActiveSheet.PivotTables(PTName).PivotFields("Product")
        .Orientation = xlPageField
        .Position = 1
    End With
    
    '5. Show Report Filter Pages
    ActiveSheet.PivotTables(PTName).ShowPages PageField:="Product"
        
End Sub

Sub CreatePivot2(SourceSheet As String)

    YrList = Array(2022, 2023)

    'DESCRIPTION: Create the Pivot Table of Type 2
    'INPUT: SourceSheet - Name of the sheet where the source data comes from
    
    'Assuming the correct sheet is selected, create Pivot Table with
    ' - Province in Rows
    ' - Years in Values
    ' - Factory in Columns
    ' - Product in Filter
    ' - Show Report Filter Pages
    
    '0. Get the Coordinates of the Source Data
    Worksheets(SourceSheet).Select
    Range("A1").End(xlDown).End(xlToRight).Select
    EndPoint = "R" & CStr(ActiveCell.Row) & "C" & CStr(ActiveCell.Column)
    
    PTName = "Pivot"
    
    '1. Insert Pivot Table
    Range("A1").Select
    Sheets.Add Before:=Worksheets(SourceSheet)
    ActiveSheet.Name = PTName
    Sheets(PTName).Select
    ActiveWorkbook.PivotCaches.Create(SourceType:=xlDatabase, SourceData:= _
        SourceSheet & "!R1C1:" & EndPoint, Version:=8).CreatePivotTable _
        TableDestination:=PTName & "!R3C1", TableName:=PTName, DefaultVersion _
        :=8
    Cells(3, 1).Select
    With ActiveSheet.PivotTables(PTName)
        .ColumnGrand = False
        .RowGrand = False
    End With
    ActiveSheet.PivotTables(PTName).RepeatAllLabels 2
    
    '2. Put Province in Rows
    With ActiveSheet.PivotTables(PTName).PivotFields("Province")
        .Orientation = xlRowField
        .Position = 1
    End With
    
    '3. Put Years in Value
    For Yr = YrList(0) To YrList(1)
        ActiveSheet.PivotTables(PTName).AddDataField ActiveSheet.PivotTables( _
        PTName).PivotFields(CStr(Yr)), "Sum of " & Yr, xlSum
    Next Yr
    
    '4. Put Factory into Columns
    With ActiveSheet.PivotTables(PTName).PivotFields("Factory")
        .Orientation = xlColumnField
        .Position = 2
    End With
    
    '4. Put Product into Filters
    With ActiveSheet.PivotTables(PTName).PivotFields("Product")
        .Orientation = xlPageField
        .Position = 1
    End With
    
    '5. Show Report Filter Pages
    ActiveSheet.PivotTables(PTName).ShowPages PageField:="Product"
        
End Sub

Sub CopyPivot(SheetName, Color1, Color2)

    NoFactory = 2
    YearList = Array(2022, 2023)
    SheetList = Array("ICF", "OCF", "OCP", "OVF", "OVP")
    ProdList = Array("Bag", "Bulk")
    
    'DESCRIPTION: Subroutine for Copying Pivot Table
    'INPUT: Name of SheetName
    
    'All Products Sheets
    Application.DisplayAlerts = False
    
    'Copy
    Sheets("Pivot").Cells(3, 1).CurrentRegion.Copy
    
    'And Paste
    Sheets.Add.Name = SheetName
    Cells(1, 1).PasteSpecial
    
    If Right(SheetName, 1) = "P" Then
        Rows(1).Delete
    End If
    
    Range("A1").Select
    
    'Change Tab Color
    ActiveSheet.Tab.Color = Color1
    
    'Delete Pivot Sheets
    Sheets("Pivot").Delete
        
    'Single Product sheet
    For Each Prod In ProdList
    
        'Copy
        Sheets(Prod).Cells(3, 1).CurrentRegion.Copy
        
        'Create New Sheet After the Current Sheet
        Sheets.Add After:=Worksheets(Prod)
        ActiveSheet.Name = SheetName & " - " & Prod
        
        'Paste
        Cells(1, 1).PasteSpecial
        
        If Right(SheetName, 1) = "P" Then
            Rows(1).Delete
        End If
        
        Sheets(SheetName & " - " & Prod).Select
        Range("A1").Select
        
        'Change Tab Color
        ActiveSheet.Tab.Color = Color2
        
        
        'Delete Pivot Sheets
        Sheets(Prod).Delete
        
    Next Prod
    
    Application.DisplayAlerts = True
    
End Sub

Sub Format()

    'DESCRIPTION: Subroutine to format sheet after postprocessing

    For Each Current In Worksheets
    
        Current.Select
        ActiveSheet.Range("A1").CurrentRegion.Select
        With Selection
            .HorizontalAlignment = xlCenter
            .VerticalAlignment = xlCenter
            .Borders.LineStyle = xlContinuous
            .Columns.AutoFit
            
        End With
        
        Range("A1").Select
        
    Next Current
        
End Sub

Sub PostProcess()

    'DESCRIPTION: All processing here

    'ICF
    Call CreatePivot1("Inbound Cost Per Factory")
    Call CopyPivot("ICF", RGB(255, 255, 255), RGB(128, 128, 128))

    'OCF
    Call CreatePivot1("Outbound Cost Per Customer")
    Call CopyPivot("OCF", RGB(255, 0, 0), RGB(255, 192, 0))
    
    'OCP
    Call CreatePivot2("Outbound Cost Per Customer")
    Call CopyPivot("OCP", RGB(255, 255, 0), RGB(0, 176, 80))
    
    'OVF
    Call CreatePivot1("Outbound Volume Per Customer")
    Call CopyPivot("OVF", RGB(0, 176, 240), RGB(0, 112, 192))
    
    'OVP
    Call CreatePivot2("Outbound Volume Per Customer")
    Call CopyPivot("OVP", RGB(0, 32, 96), RGB(112, 48, 160))
    
    'Formatting
    Call Format
    
    'Move Starters Worksheets
    Worksheets("Outbound Volume Per Customer").Move Before:=Worksheets(1)
    Worksheets("Outbound Cost Per Customer").Move Before:=Worksheets(1)
    Worksheets("Inbound Cost Per Factory").Move Before:=Worksheets(1)
    
    MsgBox "Post-Processing Completed Successfully!"
    
End Sub

'Reorder the file
'Write subroutine to format the files autofit, borders, centers and such Done
'Write message to before and after postprocessing.
