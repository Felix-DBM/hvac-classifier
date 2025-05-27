"""
HVAC Extractor (hvac_extractor.py) für HVAC Classifier
Extrahiert HVAC-Komponenten aus IFC-Dateien
"""

import ifcopenshell
import re

def ifc_type_exists(ifc_file, type_name):
    try:
        _ = ifc_file.by_type(type_name)
        return True
    except:
        return False


# Sicheres Laden von IFC-Typen (Schema-agnostisch)
def safe_by_type(ifc_file, type_name):
    try:
        return ifc_file.by_type(type_name)
    except Exception:
        return []

class HVACExtractor:
    """
    Klasse zum Extrahieren von HVAC-Komponenten aus IFC-Dateien.
    Identifiziert relevante TGA/HVAC-Elemente in einem BIM-Modell.
    """
    
    def __init__(self, ifc_file):
        """
        Initialisiert den HVAC Extractor
        
        Args:
            ifc_file: ifcopenshell.file.File Objekt der IFC-Datei
        """
        self.ifc_file = ifc_file
        

        # HVAC-relevante IFC-Typen
        self.hvac_types_all = [
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

        # Hier den Filter anwenden
        self.hvac_types = [t for t in self.hvac_types_all if ifc_type_exists(self.ifc_file, t)]

        
        # Suchbegriffe für elektronisch gesteuerte Elemente
        self.electronic_keywords = [
            "steuerung", "regler", "sensor", "fühler", "messer", "aktor", "stellantrieb",
            "thermostat", "kontroller", "regelgerät", "bediengerät", "zähler", "motor",
            "ventil", "klappe", "antrieb", "control", "electronic", "regulate", "device"
        ]
        
        # Elektronisch gesteuerte Komponenten-Typen
        self.electronic_types = [
            'IfcActuator', 'IfcAlarm', 'IfcController', 'IfcSensor', 'IfcUnitaryControlElement',
            'IfcProtectiveDeviceTrippingUnit', 'IfcFlowMeter', 'IfcElectricDistributionBoard'
        ]
    
    def extract_all_hvac_elements(self):
        """
        Extrahiert alle HVAC-Elemente aus der IFC-Datei
        
        Returns:
            list: Liste aller gefundenen HVAC-Elemente
        """
        hvac_elements = []
        
        # Durchlaufe alle HVAC-relevanten IFC-Typen
        for element_type in self.hvac_types:
            elements = safe_by_type(self.ifc_file, element_type)
            for element in elements:
                # Grundlegende Elementinformationen extrahieren
                element_info = self._extract_element_info(element)
                hvac_elements.append(element_info)
        
        return hvac_elements
    
    def extract_electronic_elements(self):
        """
        Extrahiert nur elektronisch gesteuerte HVAC-Elemente
        
        Returns:
            list: Liste der elektronisch gesteuerten HVAC-Elemente
        """
        all_elements = self.extract_all_hvac_elements()
        return [element for element in all_elements if element["is_electronic"]]
    
    def _extract_element_info(self, element):
        """
        Extrahiert Grundinformationen zu einem IFC-Element
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            dict: Grundinformationen zum Element
        """
        element_id = element.id()
        element_type = element.is_a()
        element_name = element.Name if hasattr(element, "Name") and element.Name else f"Element_{element_id}"
        
        # Prüfe, ob das Element elektronisch gesteuert ist
        is_electronic = self._is_electronic_controlled(element)
        
        # Eigenschaften extrahieren
        properties = self._extract_properties(element)
        
        # Elementmetadaten
        metadata = {
            "global_id": element.GlobalId if hasattr(element, "GlobalId") else None,
            "description": element.Description if hasattr(element, "Description") and element.Description else None
        }
        
        # Geometrische Informationen (wenn vorhanden)
        geometry = self._extract_geometry_info(element)
        
        # Materialinformationen (wenn vorhanden)
        material = self._extract_material_info(element)
        
        # Ergebnis zusammenstellen
        result = {
            "element_id": element_id,
            "element_name": element_name,
            "element_type": element_type,
            "is_electronic": is_electronic,
            "properties": properties,
            "metadata": metadata
        }
        
        # Geometrie- und Materialinformationen hinzufügen, falls vorhanden
        if geometry:
            result["geometry"] = geometry
        
        if material:
            result["material"] = material
        
        return result
    
    def _is_electronic_controlled(self, element):
        """
        Prüft, ob ein Element elektronisch gesteuert ist
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            bool: True wenn elektronisch gesteuert
        """
        # 1. Prüfe, ob der Elementtyp direkt elektronisch ist
        if element.is_a() in self.electronic_types:
            return True
        
        # 2. Prüfe Namen auf Schlüsselwörter
        if hasattr(element, "Name") and element.Name:
            for keyword in self.electronic_keywords:
                if keyword in element.Name.lower():
                    return True
        
        # 3. Prüfe Beschreibung auf Schlüsselwörter
        if hasattr(element, "Description") and element.Description:
            for keyword in self.electronic_keywords:
                if keyword in element.Description.lower():
                    return True
        
        # 4. Prüfe Eigenschaften
        properties = self._extract_properties(element)
        for prop_name, prop_value in properties.items():
            # Prüfe Eigenschaftsnamen
            for keyword in self.electronic_keywords:
                if keyword in prop_name.lower():
                    return True
            
            # Prüfe Eigenschaftswerte
            if isinstance(prop_value, str):
                for keyword in self.electronic_keywords:
                    if keyword in prop_value.lower():
                        return True
        
        # 5. Prüfe auf Beziehungen zu elektronischen Komponenten
        # (komplexere Prüfung basierend auf IFC-Beziehungen)
        if hasattr(element, "IsConnectedTo"):
            for rel in element.IsConnectedTo:
                if hasattr(rel, "RelatedElement") and rel.RelatedElement:
                    related_element = rel.RelatedElement
                    if related_element.is_a() in self.electronic_types:
                        return True
        
        return False
    
    def _extract_properties(self, element):
        """
        Extrahiert die Eigenschaften eines Elements
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            dict: Die Eigenschaften des Elements
        """
        properties = {}
        
        # Durchlaufe die PropertySets
        if hasattr(element, "IsDefinedBy"):
            for definition in element.IsDefinedBy:
                if hasattr(definition, "RelatingPropertyDefinition"):
                    prop_def = definition.RelatingPropertyDefinition
                    
                    # Einzelne Eigenschaften
                    if hasattr(prop_def, "HasProperties"):
                        for prop in prop_def.HasProperties:
                            if hasattr(prop, "Name") and hasattr(prop, "NominalValue") and prop.NominalValue:
                                prop_name = prop.Name
                                prop_value = prop.NominalValue.wrappedValue
                                properties[prop_name] = prop_value
                    
                    # Property Sets
                    if hasattr(prop_def, "Name"):
                        pset_name = prop_def.Name
                        if pset_name.startswith("Pset_") or pset_name.startswith("PSet_"):
                            properties[f"PropertySet_{pset_name}"] = True
        
        return properties
    
    def _extract_geometry_info(self, element):
        """
        Extrahiert grundlegende geometrische Informationen eines Elements
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            dict: Geometrische Informationen oder None
        """
        geometry = {}
        
        # Prüfe, ob das Element eine Objektplatzierung hat
        if hasattr(element, "ObjectPlacement") and element.ObjectPlacement:
            placement = element.ObjectPlacement
            
            # Bei lokaler Platzierung, extrahiere die Koordinaten
            if placement.is_a("IfcLocalPlacement") and hasattr(placement, "RelativePlacement"):
                rel_placement = placement.RelativePlacement
                
                if hasattr(rel_placement, "Location") and rel_placement.Location:
                    location = rel_placement.Location
                    if hasattr(location, "Coordinates") and len(location.Coordinates) >= 3:
                        geometry["position"] = {
                            "x": location.Coordinates[0],
                            "y": location.Coordinates[1],
                            "z": location.Coordinates[2]
                        }
        
        # Versuche, Bounding Box oder ähnliche Informationen zu extrahieren (wenn verfügbar)
        if hasattr(element, "Representation") and element.Representation:
            # Die Extraktion der genauen geometrischen Daten ist komplex und hängt vom IFC-Schema ab
            # Hier beschränken wir uns auf die Angabe, dass Geometrie vorhanden ist
            geometry["has_representation"] = True
        
        return geometry if geometry else None
    
    def _extract_material_info(self, element):
        """
        Extrahiert Materialinformationen eines Elements (wenn vorhanden)
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            dict: Materialinformationen oder None
        """
        materials = []
        
        # Prüfe auf Materialzuweisungen
        if hasattr(element, "HasAssociations"):
            for association in element.HasAssociations:
                if association.is_a("IfcRelAssociatesMaterial"):
                    relating_material = association.RelatingMaterial
                    
                    # Für einfache Materialien
                    if relating_material.is_a("IfcMaterial"):
                        materials.append({
                            "name": relating_material.Name,
                            "type": "single"
                        })
                    
                    # Für Materiallisten
                    elif relating_material.is_a("IfcMaterialList"):
                        for material in relating_material.Materials:
                            materials.append({
                                "name": material.Name,
                                "type": "list_item"
                            })
                    
                    # Für Materialschichten
                    elif relating_material.is_a("IfcMaterialLayerSetUsage"):
                        layer_set = relating_material.ForLayerSet
                        if layer_set and hasattr(layer_set, "MaterialLayers"):
                            for layer in layer_set.MaterialLayers:
                                if hasattr(layer, "Material") and layer.Material:
                                    materials.append({
                                        "name": layer.Material.Name,
                                        "type": "layer",
                                        "thickness": layer.LayerThickness if hasattr(layer, "LayerThickness") else None
                                    })
        
        return materials if materials else None
    
    def get_element_by_id(self, element_id):
        """
        Lädt ein Element anhand seiner ID
        
        Args:
            element_id: ID des Elements
            
        Returns:
            Element oder None wenn nicht gefunden
        """
        try:
            return self.ifc_file.by_id(element_id)
        except:
            return None
    
    def get_element_by_guid(self, guid):
        """
        Lädt ein Element anhand seiner GlobalId
        
        Args:
            guid: GlobalId des Elements
            
        Returns:
            Element oder None wenn nicht gefunden
        """
        try:
            return self.ifc_file.by_guid(guid)
        except:
            return None
    
    def search_elements_by_name(self, name_pattern):
        """
        Sucht Elemente anhand eines Namensmusters
        
        Args:
            name_pattern: Regex-Muster für den Namen
            
        Returns:
            list: Gefundene Elemente
        """
        result = []
        pattern = re.compile(name_pattern, re.IGNORECASE)
        
        for element_type in self.hvac_types:
            elements = safe_by_type(self.ifc_file, element_type)
            for element in elements:
                if hasattr(element, "Name") and element.Name and pattern.search(element.Name):
                    result.append(self._extract_element_info(element))
        
        return result
    
    def get_hvac_statistics(self):
        """
        Erstellt Statistiken über HVAC-Elemente in der IFC-Datei
        
        Returns:
            dict: Statistik-Informationen
        """
        stats = {
            "total_elements": 0,
            "electronic_elements": 0,
            "by_type": {}
        }
        
        # Zähle Elemente pro Typ
        for element_type in self.hvac_types:
            elements = safe_by_type(self.ifc_file, element_type)
            count = len(elements)
            electronic_count = sum(1 for e in elements if self._is_electronic_controlled(e))
            
            if count > 0:
                stats["by_type"][element_type] = {
                    "total": count,
                    "electronic": electronic_count
                }
                
                stats["total_elements"] += count
                stats["electronic_elements"] += electronic_count
        
        return stats