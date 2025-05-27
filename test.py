import ifcopenshell

# Pfad zur Datei anpassen
ifc_file = ifcopenshell.open(r"C:\Users\felix\Downloads\Building-Hvac.ifc")

hvac_types = [
    "IfcDuctSegment", "IfcDuctFitting", "IfcDuctAccessory",
    "IfcPipeSegment", "IfcPipeFitting", "IfcPipeAccessory",
    "IfcAirTerminal", "IfcAirTerminalBox", "IfcDamper", "IfcFan",
    "IfcFilter", "IfcFireDamper", "IfcSmokeDetector", "IfcHumidifier",
    "IfcSensor", "IfcValve", "IfcCompressor", "IfcBoiler", "IfcChiller",
    "IfcCoolingTower", "IfcHeatExchanger", "IfcPump", "IfcUnitaryEquipment"
]

for element_type in hvac_types:
    try:
        elements = ifc_file.by_type(element_type)
        print(f"{element_type}: {len(elements)} gefunden")
    except Exception as e:
        print(f"{element_type}: Fehler - {e}")

print("test")