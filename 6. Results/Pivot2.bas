Attribute VB_Name = "Pivot2"
Sub Pivot2()
'
' Pivot2 Macro
'

'

    '1. Insert Pivot Table
    Range("A1").Select
    Application.CutCopyMode = False
    Sheets.Add
    ActiveWorkbook.Worksheets("OBV").PivotTables("PivotTable8").PivotCache. _
        CreatePivotTable TableDestination:="Sheet9!R3C1", TableName:="PivotTable9" _
        , DefaultVersion:=8
    Sheets("Sheet9").Select
    Cells(3, 1).Select
    With ActiveSheet.PivotTables("PivotTable9")
        .ColumnGrand = True ' Make this False
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
        .RowGrand = True 'Make this False
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
    With ActiveSheet.PivotTables("PivotTable9").PivotCache
        .RefreshOnFileOpen = False
        .MissingItemsLimit = xlMissingItemsDefault
    End With
    ActiveSheet.PivotTables("PivotTable9").RepeatAllLabels 2
    
    '2. Put Years in Values
    ActiveSheet.PivotTables("PivotTable9").AddDataField ActiveSheet.PivotTables( _
        "PivotTable9").PivotFields("2022"), "Sum of 2022", xlSum
    ActiveSheet.PivotTables("PivotTable9").AddDataField ActiveSheet.PivotTables( _
        "PivotTable9").PivotFields("2023"), "Sum of 2023", xlSum
        
    '3. Put Factory in Columns
    With ActiveSheet.PivotTables("PivotTable9").PivotFields("Factory")
        .Orientation = xlColumnField
        .Position = 2
    End With
    
    '4. Put Province in Rows
    With ActiveSheet.PivotTables("PivotTable9").PivotFields("Province")
        .Orientation = xlRowField
        .Position = 1
    End With
    
    '5. Put Product in Filter
    With ActiveSheet.PivotTables("PivotTable9").PivotFields("Product")
        .Orientation = xlPageField
        .Position = 1
    End With
    
    '6. Show Report Fitler Page
    ActiveSheet.PivotTables("PivotTable9").ShowPages PageField:="Product"
    
End Sub


