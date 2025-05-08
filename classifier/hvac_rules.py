# Hier werden Klassifizierungsregeln definiert.

classification_map = {
    ("IfcFlowTerminal", None): "Luftauslass",
    ("IfcPipeSegment", None): "Rohrsegment",
    # Weitere Regeln hinzufügen...
}

def categorize(element):
    cls = element.is_a()
    pre = getattr(element, "PredefinedType", None)
    return classification_map.get((cls, pre), "Unbekannte Kategorie")
