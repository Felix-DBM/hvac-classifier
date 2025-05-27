import ifcopenshell

# Öffne die IFC-Datei (Pfad ggf. anpassen)
ifc_file = ifcopenshell.open(r"C:\Users\felix\Downloads\Building-Hvac.ifc")

# Liste der HVAC-IFC-Typen
hvac_types = [
    'IfcDuctSegment',            # Luftkanalabschnitt
    'IfcPipeSegment',            # Rohrabschnitt
    'IfcDuctFitting',            # Luftkanalverbindungsstück
    'IfcPipeFitting',            # Rohrverbindungsstück
    'IfcDuctAccessory',          # Zubehör für Luftkanäle
    'IfcPipeAccessory',          # Zubehör für Rohre
    'IfcDuctSilencer',           # Schalldämpfer
    'IfcDuctDamper',             # Drosselklappe
    'IfcFireDamper',             # Brandschutzklappe
    'IfcValve',                  # Ventil
    'IfcFan',                    # Ventilator
    'IfcPump',                   # Pumpe
    'IfcAirTerminal',            # Luftauslass, -einlass
    'IfcAirTerminalBox',         # Luftauslassbox
    'IfcHumidifier',             # Befeuchter
    'IfcFilter',                 # Filter
    'IfcChiller',                # Kältemaschine
    'IfcBoiler',                 # Heizkessel
    'IfcCoolingTower',           # Kühlturm
    'IfcCompressor',             # Kompressor
    'IfcHeatExchanger',          # Wärmetauscher
    'IfcFlowController',         # Ventile, Klappen, etc.
    'IfcFlowFitting',            # Verbindungsstücke, Übergänge
    'IfcFlowMovingDevice',       # Pumpen, Ventilatoren
    'IfcFlowSegment',            # Rohre, Kanäle
    'IfcFlowStorageDevice',      # Tanks, Speicher
    'IfcFlowTerminal',           # Auslässe, Einlässe
    'IfcFlowTreatmentDevice',    # Filter, Kühler, Heizregister
    'IfcEnergyConversionDevice', # Kessel, Wärmetauscher
    'IfcSensor',                 # Sensoren
    'IfcActuator',               # Aktoren
    'IfcController',             # Steuerungen, Regler
    'IfcUnitaryControlElement',  # Steuergeräte
    'IfcDistributionElement',    # Allgemeine Versorgungselemente
    'IfcDistributionControlElement' # Steuerelemente für Versorgungssysteme
]

print("\n--- Abfrage aller HVAC-Komponenten in der IFC-Datei ---\n")

gesamt = 0

for element_type in hvac_types:
    try:
        elements = ifc_file.by_type(element_type)
        anzahl = len(elements)
        gesamt += anzahl
        print(f"{element_type}: {anzahl} gefunden")
    except Exception as e:
        print(f"{element_type}: Fehler - {e}")

print(f"\nGesamtzahl aller gefundenen HVAC-Elemente: {gesamt}\n")
