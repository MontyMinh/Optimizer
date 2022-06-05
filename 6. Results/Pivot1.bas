Attribute VB_Name = "Pivot1"
Sub Pivot1()
'
' Pivot1 Macro
'

    '1. Insert Pivot Table
    Range("A1").Select
    Application.CutCopyMode = False
    Sheets.Add
    ActiveWorkbook.Worksheets("OBV").PivotTables("PivotTable8").PivotCache. _
        CreatePivotTable TableDestination:="Sheet3!R3C1", TableName:="PivotTable3" _
        , DefaultVersion:=8
    Sheets("Sheet3").Select
    Cells(3, 1).Select
    With ActiveSheet.PivotTables("PivotTable3")
        .ColumnGrand = True 'Put False here
        .HasAutoFormat = True
        .DisplayErrorString = False
        .DisplayNullString = True
        .EnableDrilldown = True
        .ErrorString = ""
        .MergeLabels = False
        .NullString = ""
        .PageFieldOrder = 2
        .PageFieldWrapCount = 0
        .PreserveFormatting = True
        .RowGrand = True
        .SaveData = True
        .PrintTitles = False
        .RepeatItemsOnEachPrintedPage = True
        .TotalsAnnotation = False
        .CompactRowIndent = 1
        .InGridDropZones = False
        .DisplayFieldCaptions = True
        .DisplayMemberPropertyTooltips = False
        .DisplayContextTooltips = True
        .ShowDrillIndicators = True
        .PrintDrillIndicators = False
        .AllowMultipleFilters = False
        .SortUsingCustomLists = True
        .FieldListSortAscending = True
        .ShowValuesRow = False
        .CalculatedMembersInFilters = False
        .RowAxisLayout xlOutlineRow
    End With
    With ActiveSheet.PivotTables("PivotTable3").PivotCache
        .RefreshOnFileOpen = False
        .MissingItemsLimit = xlMissingItemsDefault
    End With
    ActiveSheet.PivotTables("PivotTable3").RepeatAllLabels 2
    
    '2. Put Factory in Rows
    With ActiveSheet.PivotTables("PivotTable3").PivotFields("Factory")
        .Orientation = xlRowField
        .Position = 1
    End With
    
    '3. Put Years in Value
    ActiveSheet.PivotTables("PivotTable3").AddDataField ActiveSheet.PivotTables( _
        "PivotTable3").PivotFields("2022"), "Sum of 2022", xlSum
    ActiveSheet.PivotTables("PivotTable3").AddDataField ActiveSheet.PivotTables( _
        "PivotTable3").PivotFields("2023"), "Sum of 2023", xlSum
        
    '4. Put Product in Filters
    With ActiveSheet.PivotTables("PivotTable3").PivotFields("Product")
        .Orientation = xlPageField
        .Position = 1
    End With
    
    '5. Show Report Filter Pages
    ActiveSheet.PivotTables("PivotTable3").ShowPages PageField:="Product"
    Sheets("Sheet3").Select
    
End Sub




















































