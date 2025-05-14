"""
BAS-Code Konverter (bas_converter.py) für HVAC Classifier
Konvertiert zwischen verschiedenen BAS-Standards (AMEV/VDI)
"""

class BASConverter:
    """
    Klasse zur Konvertierung von BAS-Codes zwischen verschiedenen Standards.
    Unterstützt die Konvertierung zwischen AMEV und VDI 3814.
    """
    
    def __init__(self):
        """
        Initialisiert den BAS-Converter
        """
        pass
    
    def convert_amev_to_vdi(self, amev_code):
        """
        Konvertiert einen AMEV-BAS-Code in einen VDI 3814-BAS-Code
        
        Args:
            amev_code: AMEV-BAS-Code
            
        Returns:
            str: VDI 3814-BAS-Code
        """
        # Überprüfe, ob es sich um einen gültigen AMEV-Code handelt
        if not amev_code or not isinstance(amev_code, str):
            return ""
        
        # Parsen des AMEV-Codes
        parts = amev_code.split('_')
        if len(parts) < 5:
            return amev_code  # Nicht genug Teile für eine korrekte Konvertierung
        
        # Extrahiere relevante Teile für VDI-Code
        gewerk = parts[0]           # Gewerk (z.B. HEI)
        anlage = parts[1]           # Anlage (z.B. 01)
        
        # Position und Raum extrahieren (falls vorhanden)
        position = ""
        raum = ""
        for part in parts:
            if part.startswith('S') and len(part) >= 3:
                position = part[1:3]  # Stockwerk (z.B. 01 von S001)
            elif part.startswith('R') and len(part) >= 3:
                raum = part[1:3]      # Raum (z.B. 05 von R105)
        
        # VDI-Standardwerte
        funktion = "U1"
        zusatz = "101"
        
        # Erstelle VDI-Code
        vdi_code = f"{gewerk}_{anlage}_S{position}_R{raum}_{funktion}_{zusatz}"
        
        return vdi_code
    
    def convert_vdi_to_amev(self, vdi_code):
        """
        Konvertiert einen VDI 3814-BAS-Code in einen AMEV-BAS-Code
        
        Args:
            vdi_code: VDI 3814-BAS-Code
            
        Returns:
            str: AMEV-BAS-Code
        """
        # Überprüfe, ob es sich um einen gültigen VDI-Code handelt
        if not vdi_code or not isinstance(vdi_code, str):
            return ""
        
        # Parsen des VDI-Codes
        parts = vdi_code.split('_')
        if len(parts) < 4:
            return vdi_code  # Nicht genug Teile für eine korrekte Konvertierung
        
        # Extrahiere relevante Teile für AMEV-Code
        gewerk = parts[0]           # Gewerk (z.B. HEI)
        anlage = parts[1]           # Anlage (z.B. 01)
        
        # Position und Raum extrahieren (falls vorhanden)
        position = "000"
        raum = "000"
        for part in parts:
            if part.startswith('S') and len(part) >= 2:
                position = part[1:].zfill(3)  # Stockwerk (z.B. 001 von S1)
            elif part.startswith('R') and len(part) >= 2:
                raum = part[1:].zfill(3)      # Raum (z.B. 105 von R5)
        
        # AMEV-Standardwerte
        baugruppe = "ERH"
        medium = "HZV"
        betriebsmittel = "T~~01"
        funktion = "MW-01"
        erw_funktion = "TL"
        
        # Erstelle AMEV-Code
        amev_code = f"{gewerk}_{anlage}_{baugruppe}_{medium}_S{position}_R{raum}_{betriebsmittel}_{funktion}_{erw_funktion}"
        
        return amev_code