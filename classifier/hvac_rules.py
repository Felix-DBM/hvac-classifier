"""
HVAC Rules (hvac_rules.py) für HVAC Classifier
Regeln zur Klassifizierung von HVAC-Komponenten in BIM-Modellen
"""

import re
import os
import json

# Sicheres Laden von IFC-Typen (Schema-agnostisch)
def safe_by_type(ifc_file, type_name):
    try:
        return ifc_file.by_type(type_name)
    except Exception:
        return []

class HVACClassifier:
    """
    Hauptklasse zur Klassifizierung von HVAC-Komponenten in IFC-Dateien
    gemäß VDI BAS und AMEV BAS Standards.
    """
    
    def __init__(self, ifc_file, location_extractor, rules_file=None):
        """
        Initialisiert den HVAC Classifier
        
        Args:
            ifc_file: ifcopenshell.file.File Objekt der IFC-Datei
            location_extractor: LocationExtractor Instanz
            rules_file: Optional - Pfad zu einer JSON-Datei mit Klassifizierungsregeln
        """
        self.ifc_file = ifc_file
        self.location_extractor = location_extractor
        self.rules = self._load_rules(rules_file)
        
        # HVAC-spezifische IFC-Typen
        self.hvac_types = [
            'IfcFlowController',    # Ventile, Klappen, etc.
            'IfcFlowFitting',       # Verbindungsstücke, Übergänge
            'IfcFlowMovingDevice',  # Pumpen, Ventilatoren
            'IfcFlowSegment',       # Rohre, Kanäle
            'IfcFlowStorageDevice', # Tanks, Speicher
            'IfcFlowTerminal',      # Auslässe, Einlässe
            'IfcFlowTreatmentDevice', # Filter, Kühler, Heizregister
            'IfcEnergyConversionDevice', # Kessel, Wärmetauscher
            'IfcSensor',            # Sensoren
            'IfcActuator',          # Aktoren
            'IfcController',        # Steuerungen, Regler
            'IfcUnitaryControlElement', # Steuergeräte
        ]
        
        # Elektronisch gesteuerte Komponenten-Typen
        self.electronic_types = [
            'IfcActuator', 'IfcAlarm', 'IfcController', 'IfcSensor', 'IfcUnitaryControlElement',
            'IfcProtectiveDeviceTrippingUnit', 'IfcFlowMeter', 'IfcElectricDistributionBoard'
        ]
        
        # Suchbegriffe für elektronisch gesteuerte Elemente
        self.electronic_keywords = [
            "steuerung", "regler", "sensor", "fühler", "messer", "aktor", "stellantrieb",
            "thermostat", "kontroller", "regelgerät", "bediengerät", "zähler", "motor",
            "ventil", "klappe", "antrieb", "control", "electronic", "regulate", "device"
        ]
        
        # Gewerk-Code Mapping
        self.gewerk_mapping = {
            "IfcFlowController": "REG",       # Regelung
            "IfcFlowMovingDevice": "LTA",      # Lüftungstechnik
            "IfcFlowTerminal": "LTA",          # Lüftungstechnik
            "IfcEnergyConversionDevice": "HEI", # Heizung
            "IfcFlowFitting": "SAN",           # Sanitär
            "IfcFlowSegment": "KLI",           # Klima
            "IfcFlowStorageDevice": "KLI",      # Klima
            "IfcFlowTreatmentDevice": "KLI",    # Klima
            "IfcSensor": "REG",                # Regelung
            "IfcActuator": "REG",              # Regelung
            "IfcController": "REG",            # Regelung
            "IfcUnitaryControlElement": "REG",  # Regelung
            "DEFAULT": "XXX"                   # Unbekannt
        }
    
    def _load_rules(self, rules_file):
        """
        Lädt Klassifizierungsregeln aus einer JSON-Datei
        
        Args:
            rules_file: Pfad zur JSON-Datei mit Regeln
            
        Returns:
            dict: Die geladenen Regeln
        """
        # Standardregeln
        default_rules = {
            "electronic_components": {
                "types": [
                    'IfcActuator', 'IfcAlarm', 'IfcController', 'IfcSensor', 'IfcUnitaryControlElement'
                ],
                "keywords": [
                    "steuerung", "regler", "sensor", "fühler", "messer", "aktor", "stellantrieb",
                    "thermostat", "kontroller", "regelgerät", "bediengerät", "zähler", "motor",
                    "ventil", "klappe", "antrieb", "control", "electronic", "regulate", "device"
                ]
            },
            "type_mapping": {
                "IfcFlowController": {
                    "gewerk": "REG",
                    "code_prefix": "VEN"
                },
                "IfcFlowMovingDevice": {
                    "gewerk": "LTA", 
                    "code_prefix": "VEN"
                },
                "IfcFlowTerminal": {
                    "gewerk": "LTA",
                    "code_prefix": "AUS"
                },
                "IfcEnergyConversionDevice": {
                    "gewerk": "HEI",
                    "code_prefix": "KES"
                },
                "IfcSensor": {
                    "gewerk": "REG",
                    "code_prefix": "SEN"
                },
                "IfcActuator": {
                    "gewerk": "REG",
                    "code_prefix": "AKT"
                },
                "IfcController": {
                    "gewerk": "REG",
                    "code_prefix": "REG"
                }
            }
        }
        
        # Wenn keine Datei angegeben, Standardregeln verwenden
        if not rules_file:
            return default_rules
        
        # Überprüfen, ob die Datei existiert
        if not os.path.exists(rules_file):
            print(f"Warnung: Regeldatei {rules_file} nicht gefunden. Verwende Standardregeln.")
            return default_rules
        
        # Versuche, die Datei zu laden
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                custom_rules = json.load(f)
                
                # Kombiniere mit Standardregeln
                for key, value in custom_rules.items():
                    if key in default_rules and isinstance(value, dict):
                        default_rules[key].update(value)
                    else:
                        default_rules[key] = value
                
                return default_rules
        
        except Exception as e:
            print(f"Fehler beim Laden der Regeldatei: {str(e)}")
            return default_rules
    
    def classify_all_hvac_elements(self, standard="amev", electronic_only=True):
        """
        Klassifiziert alle HVAC-Elemente in der IFC-Datei
        
        Args:
            standard: "amev" oder "vdi"
            electronic_only: Nur elektronisch gesteuerte Elemente beachten
            
        Returns:
            dict: {
                "flat_results": Liste aller klassifizierten Elemente,
                "hierarchy": Hierarchische Struktur der Elemente nach Standort
            }
        """
        results = []
        hierarchy = {}
        
        # Alle HVAC-Elemententypen durchgehen
        for element_type in self.hvac_types:
            elements = safe_by_type(self.ifc_file, element_type)
            for element in elements:
                # Element klassifizieren
                result = self.classify_element(element, standard, electronic_only)
                if result:
                    # In hierarchische Struktur einfügen
                    self._add_to_hierarchy(hierarchy, result)
                    results.append(result)
        
        # Ergebnisse sortieren und zurückgeben
        sorted_results = sorted(results, key=lambda x: (
            x.get('location', {}).get('storey_name', ''),
            x.get('location', {}).get('space_name', ''),
            x.get('element_name', '')
        ))
        
        return {
            "flat_results": sorted_results,
            "hierarchy": hierarchy
        }
    
    def classify_element(self, element, standard="amev", electronic_only=True):
        """
        Klassifiziert ein einzelnes HVAC-Element
        
        Args:
            element: Ein IFC-Element
            standard: "amev" oder "vdi"
            electronic_only: Nur elektronisch gesteuerte Elemente beachten
            
        Returns:
            dict: Klassifizierungsergebnis oder None wenn nicht klassifizierbar
        """
        # Elementinformationen extrahieren
        element_id = element.id()
        element_type = element.is_a()
        element_name = element.Name if hasattr(element, "Name") and element.Name else f"Element_{element_id}"
        
        # Prüfen, ob es ein HVAC-Element ist
        if element_type not in self.hvac_types:
            return None
        
        # Prüfen, ob es elektronisch gesteuert ist
        is_electronic = self._is_electronic_controlled(element)
        
        # Wenn nur elektronisch gesteuerte Elemente berücksichtigt werden sollen
        if electronic_only and not is_electronic:
            return None
        
        # Eigenschaften extrahieren
        properties = self._extract_properties(element)
        
        # Standortinformationen ermitteln
        location = self.location_extractor.get_element_location(element)
        
        # BAS-Code generieren
        bas_code = self._generate_bas_code(element, element_type, location, standard)
        
        # Ergebnis zusammenstellen
        result = {
            "element_id": element_id,
            "element_name": element_name,
            "element_type": element_type,
            "is_electronic": is_electronic,
            "bas_code": bas_code,
            "standard": standard,
            "properties": properties
        }
        
        # Standortinformationen hinzufügen, falls vorhanden
        if location:
            result["location"] = location
        
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
        
        # 3. Prüfe Eigenschaften
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
        
        # 4. Prüfe auf Beziehungen zu elektronischen Komponenten
        # (komplexere Prüfung basierend auf IFC-Beziehungen)
        
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
    
    def _generate_bas_code(self, element, element_type, location, standard):
        """
        Generiert einen BAS-Code basierend auf Element und Standort
        
        Args:
            element: Ein IFC-Element
            element_type: Typ des Elements
            location: Standortinformationen
            standard: "amev" oder "vdi"
            
        Returns:
            str: Der generierte BAS-Code
        """
        # 1. Gewerk und Anlagennummer bestimmen
        gewerk_code = self._determine_gewerk_code(element_type)
        anlage_code = self._determine_anlage_code(element)
        
        # 2. Standortinformationen extrahieren
        storey_code = "000"
        room_code = "000"
        
        if location:
            # Stockwerkcode extrahieren (aus Stockwerksnamen)
            if location.get("storey_name"):
                numeric_parts = re.findall(r'\d+', location["storey_name"])
                if numeric_parts:
                    storey_code = numeric_parts[0].zfill(3)
            
            # Raumcode extrahieren (aus Raumnamen)
            if location.get("space_name"):
                numeric_parts = re.findall(r'\d+', location["space_name"])
                if numeric_parts:
                    room_code = numeric_parts[0].zfill(3)
        
        # 3. BAS-Code je nach Standard generieren
        if standard.lower() == "amev":
            # AMEV: Gewerk_Anlage_Baugruppe_Medium_Position_Aggregat_Betriebsmittel_Funktion_ErwFunktion
            code_parts = [
                gewerk_code,                      # Gewerk (z.B. HEI für Heizung)
                anlage_code,                      # Anlage (z.B. 01 für Anlage 1)
                "ERH",                            # Baugruppe (Standard: Erzeuger)
                "HZV",                            # Medium (Standard: Heizung/Versorgung)
                f"S{storey_code}",                # Position mit Stockwerksnummer
                f"R{room_code}",                  # Aggregat mit Raumnummer
                "T~~01",                          # Betriebsmittel (Standard)
                "MW-01",                          # Funktion (Standard: Messwert)
                "TL"                              # Erweiterung Funktion (Standard)
            ]
        else:
            # VDI: Gewerk_Anlage_Betriebsmittel_Aggregat_Funktion_Zusatz
            code_parts = [
                gewerk_code,                      # Gewerk
                anlage_code,                      # Anlage
                f"S{storey_code[:2]}",            # Betriebsmittel mit Geschosscode
                f"R{room_code[:2]}",              # Aggregat mit Raumcode
                "U1",                             # Funktion (Standard)
                "101"                             # Zusatz (Standard)
            ]
        
        return '_'.join(code_parts)
    
    def _determine_gewerk_code(self, element_type):
        """
        Bestimmt den Gewerk-Code basierend auf dem Elementtyp
        
        Args:
            element_type: IFC-Elementtyp
            
        Returns:
            str: Gewerk-Code
        """
        return self.gewerk_mapping.get(element_type, self.gewerk_mapping.get("DEFAULT"))
    
    def _determine_anlage_code(self, element):
        """
        Bestimmt den Anlagen-Code basierend auf dem Element
        
        Args:
            element: IFC-Element
            
        Returns:
            str: Anlagen-Code
        """
        # Versuche, aus dem Namen eine Anlagennummer zu extrahieren
        if hasattr(element, "Name") and element.Name:
            numeric_parts = re.findall(r'\d+', element.Name)
            if numeric_parts:
                # Verwende die erste gefundene Zahl
                anlage_num = int(numeric_parts[0]) % 100  # Modulo 100 um zweistellig zu halten
                return f"{anlage_num:02d}"
        
        # Fallback: Verwende die Element-ID modulo 100
        anlage_num = element.id() % 100
        return f"{anlage_num:02d}"
    
    def _add_to_hierarchy(self, hierarchy, result):
        """
        Fügt ein klassifiziertes Element zur hierarchischen Struktur hinzu
        
        Args:
            hierarchy: Die hierarchische Struktur
            result: Das Klassifizierungsergebnis
        """
        location = result.get("location", {})
        storey_name = location.get("storey_name", "Unbekanntes Geschoss")
        storey_id = location.get("storey_id")
        space_name = location.get("space_name")
        space_id = location.get("space_id")
        
        # Geschoss hinzufügen, falls noch nicht vorhanden
        if storey_name not in hierarchy:
            hierarchy[storey_name] = {
                "id": storey_id,
                "name": storey_name,
                "type": "storey",
                "children": {}
            }
        
        # Wenn Raum vorhanden, Element zum Raum hinzufügen
        if space_name:
            # Raum hinzufügen, falls noch nicht vorhanden
            if space_name not in hierarchy[storey_name]["children"]:
                hierarchy[storey_name]["children"][space_name] = {
                    "id": space_id,
                    "name": space_name,
                    "type": "space",
                    "children": {}
                }
            
            # Element dem Raum hinzufügen
            element_id = str(result["element_id"])
            hierarchy[storey_name]["children"][space_name]["children"][element_id] = {
                "id": result["element_id"],
                "name": result["element_name"],
                "type": result["element_type"],
                "bas_code": result["bas_code"],
                "is_electronic": result["is_electronic"]
            }
        else:
            # Element direkt dem Geschoss hinzufügen, wenn kein Raum vorhanden
            element_id = str(result["element_id"])
            hierarchy[storey_name]["children"][element_id] = {
                "id": result["element_id"],
                "name": result["element_name"],
                "type": result["element_type"],
                "bas_code": result["bas_code"],
                "is_electronic": result["is_electronic"]
            }