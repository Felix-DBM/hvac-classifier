"""
Location Extractor (location_extractor.py) für HVAC Classifier
Extrahiert Standortinformationen aus IFC-Dateien
"""

class LocationExtractor:
    """
    Klasse zur Extraktion von Standortinformationen (Stockwerk, Raum) aus IFC-Dateien
    für die Verwendung im BAS-Code.
    """
    
    def __init__(self, ifc_file):
        """
        Initialisiert den LocationExtractor
        
        Args:
            ifc_file: ifcopenshell.file.File Objekt der IFC-Datei
        """
        self.ifc_file = ifc_file
        self.building_storeys = {}  # storey_id -> {name, elevation}
        self.spaces = {}  # space_id -> {name, storey_id}
        self._extract_storeys()
        self._extract_spaces()
        
    def _extract_storeys(self):
        """Extrahiert alle Geschosse aus der IFC-Datei"""
        storeys = self.ifc_file.by_type("IfcBuildingStorey")
        for storey in storeys:
            storey_id = storey.id()
            name = storey.Name if hasattr(storey, "Name") and storey.Name else f"Geschoss {storey_id}"
            elevation = storey.Elevation if hasattr(storey, "Elevation") else 0.0
            
            self.building_storeys[storey_id] = {
                "name": name,
                "elevation": elevation
            }
            
    def _extract_spaces(self):
        """Extrahiert alle Räume aus der IFC-Datei"""
        spaces = self.ifc_file.by_type("IfcSpace")
        for space in spaces:
            space_id = space.id()
            name = space.Name if hasattr(space, "Name") and space.Name else f"Raum {space_id}"
            
            # Finde das zugehörige Geschoss
            storey_id = None
            if hasattr(space, "Decomposes"):
                for rel in space.Decomposes:
                    if hasattr(rel, "RelatingObject") and rel.RelatingObject.is_a("IfcBuildingStorey"):
                        storey_id = rel.RelatingObject.id()
                        break
            
            self.spaces[space_id] = {
                "name": name,
                "storey_id": storey_id
            }
    
    def get_element_location(self, element):
        """
        Ermittelt den Standort eines Elements (Geschoss und Raum)
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            dict: {storey_name, storey_id, space_name, space_id} oder None wenn nicht gefunden
        """
        # Finde den Raum, in dem sich das Element befindet
        space_id = self._find_containing_space(element)
        
        if space_id and space_id in self.spaces:
            space = self.spaces[space_id]
            storey_id = space["storey_id"]
            
            if storey_id and storey_id in self.building_storeys:
                return {
                    "storey_name": self.building_storeys[storey_id]["name"],
                    "storey_id": storey_id,
                    "space_name": space["name"],
                    "space_id": space_id
                }
            elif storey_id:
                # Geschoss nicht gefunden, aber ID bekannt
                return {
                    "storey_name": f"Geschoss {storey_id}",
                    "storey_id": storey_id,
                    "space_name": space["name"],
                    "space_id": space_id
                }
        
        # Versuche, direkt das Geschoss zu finden
        storey_id = self._find_containing_storey(element)
        if storey_id and storey_id in self.building_storeys:
            return {
                "storey_name": self.building_storeys[storey_id]["name"],
                "storey_id": storey_id,
                "space_name": None,
                "space_id": None
            }
        
        return None
    
    def _find_containing_space(self, element):
        """
        Findet den Raum, der das Element enthält
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            int: ID des Raums oder None wenn nicht gefunden
        """
        # Methode 1: Prüfe auf IfcRelContainedInSpatialStructure
        if hasattr(element, "ContainedInStructure"):
            for rel in element.ContainedInStructure:
                if hasattr(rel, "RelatingStructure") and rel.RelatingStructure.is_a("IfcSpace"):
                    return rel.RelatingStructure.id()
        
        # Methode 2: Über Dekomposition (weniger genau)
        if hasattr(element, "Decomposes"):
            for rel in element.Decomposes:
                if hasattr(rel, "RelatingObject") and rel.RelatingObject.is_a("IfcSpace"):
                    return rel.RelatingObject.id()
        
        # Methode 3: Prüfe auf räumliche Zuordnung durch IfcRelSpaceBoundary
        boundaries = self.ifc_file.by_type("IfcRelSpaceBoundary")
        for boundary in boundaries:
            if hasattr(boundary, "RelatedBuildingElement") and boundary.RelatedBuildingElement == element:
                if hasattr(boundary, "RelatingSpace") and boundary.RelatingSpace.is_a("IfcSpace"):
                    return boundary.RelatingSpace.id()
        
        return None
    
    def _find_containing_storey(self, element):
        """
        Findet das Geschoss, das das Element enthält
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            int: ID des Geschosses oder None wenn nicht gefunden
        """
        # Methode 1: Prüfe auf direkte Beziehung zu einem Geschoss
        if hasattr(element, "ContainedInStructure"):
            for rel in element.ContainedInStructure:
                if hasattr(rel, "RelatingStructure"):
                    relating_structure = rel.RelatingStructure
                    if relating_structure.is_a("IfcBuildingStorey"):
                        return relating_structure.id()
                    elif hasattr(relating_structure, "Decomposes"):
                        for decomp in relating_structure.Decomposes:
                            if hasattr(decomp, "RelatingObject") and decomp.RelatingObject.is_a("IfcBuildingStorey"):
                                return decomp.RelatingObject.id()
        
        # Methode 2: Über Dekomposition (weniger genau)
        if hasattr(element, "Decomposes"):
            for rel in element.Decomposes:
                if hasattr(rel, "RelatingObject"):
                    relating_obj = rel.RelatingObject
                    if relating_obj.is_a("IfcBuildingStorey"):
                        return relating_obj.id()
                    elif hasattr(relating_obj, "Decomposes"):
                        for decomp in relating_obj.Decomposes:
                            if hasattr(decomp, "RelatingObject") and decomp.RelatingObject.is_a("IfcBuildingStorey"):
                                return decomp.RelatingObject.id()
        
        # Methode 3: Bestimme das Geschoss basierend auf Höhenlage (könnte ungenau sein)
        if hasattr(element, "ObjectPlacement") and element.ObjectPlacement:
            element_z = self._get_element_z_coordinate(element)
            if element_z is not None:
                # Finde das passende Geschoss basierend auf der Z-Koordinate
                best_storey_id = None
                best_elevation = float('-inf')
                
                for storey_id, storey in self.building_storeys.items():
                    if storey["elevation"] <= element_z and storey["elevation"] > best_elevation:
                        best_elevation = storey["elevation"]
                        best_storey_id = storey_id
                
                return best_storey_id
        
        return None
    
    def _get_element_z_coordinate(self, element):
        """
        Versucht, die Z-Koordinate (Höhe) eines Elements zu ermitteln
        
        Args:
            element: Ein IFC-Element
            
        Returns:
            float: Z-Koordinate oder None wenn nicht ermittelbar
        """
        try:
            if hasattr(element, "ObjectPlacement") and element.ObjectPlacement:
                placement = element.ObjectPlacement
                
                # Verschiedene Arten von Platzierungen verarbeiten
                if placement.is_a("IfcLocalPlacement") and hasattr(placement, "RelativePlacement"):
                    rel_placement = placement.RelativePlacement
                    
                    if hasattr(rel_placement, "Location"):
                        location = rel_placement.Location
                        if hasattr(location, "Coordinates"):
                            # Die dritte Koordinate ist in der Regel Z (Höhe)
                            if len(location.Coordinates) >= 3:
                                return location.Coordinates[2]
            
            return None
        
        except Exception:
            return None