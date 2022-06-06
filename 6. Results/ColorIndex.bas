Attribute VB_Name = "ColorIndex"
Function getColor(Rng As Range, ByVal ColorFormat As String) As Variant
    Dim ColorValue As Variant
    ColorValue = Cells(Rng.Row, Rng.Column).Interior.Color
    Select Case LCase(ColorFormat)
        Case "index"
            getColor = Rng.Interior.ColorIndex
        Case "rgb"
            getColor = (ColorValue Mod 256) & ", " & ((ColorValue \ 256) Mod 256) & ", " & (ColorValue \ 65536)
        Case Else
            getColor = "Only use 'Index' or 'RGB' as second argument!"
    End Select
End Function

