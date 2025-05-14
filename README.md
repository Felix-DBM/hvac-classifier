"""
Aktualisierte README.md mit neuen Funktionen und Strukturinformationen
"""

# HVAC Classifier

**Prototyp zur automatischen Kategorisierung von HVAC-Komponenten in BIM-Modellen**

---

## 📋 Inhaltsverzeichnis

1. [Projektübersicht](#projektübersicht)
2. [Hauptfunktionen](#hauptfunktionen)
3. [Voraussetzungen](#voraussetzungen)
4. [Installation](#installation)
5. [Projektstruktur](#projektstruktur)
6. [Erste Schritte](#erste-schritte)
7. [Architektur](#architektur)
8. [Roadmap](#roadmap)
9. [Lizenz](#lizenz)

---

## Projektübersicht

In diesem Projekt wird ein Prototyp entwickelt, der **HVAC-Komponenten** (Heizung, Lüftung, Klima) in digitalen Bauwerksmodellen automatisch erkennt und gemäß den deutschen Standards **BACTwin** und **AMEV** kategorisiert. Durch die Automatisierung wird der manuelle Aufwand minimiert, Fehlerraten reduziert und eine einheitliche Klassifizierung sichergestellt.

## Hauptfunktionen

* **IFC-Import**: Einlesen und Verarbeiten von BIM-Modellen im IFC-Format
* **Standorterkennung**: Automatische Extraktion von Stockwerk- und Rauminformationen
* **Erkennung**: Identifikation relevanter HVAC-Elemente (z. B. Luftauslässe, Heizkörper, Ventile)
* **Elektronik-Erkennung**: Identifikation elektronisch gesteuerter Komponenten
* **Klassifizierung**: Zuordnung gemäß BACTwin- und AMEV-Standard mit integrierter Standortinformation im BAS-Code
* **Dual-Ansicht**: Darstellung der Ergebnisse als Baumstruktur und Tabelle
* **Ausgabeoptionen**: Ergebnisse wahlweise in der Konsole oder in einer Weboberfläche (Flask)

## Voraussetzungen

* **Python** 3.8 oder neuer
* **PostgreSQL** Datenbank
* **ifcopenshell** zum Parsen von IFC-Dateien
* **Flask** für die Weboberfläche

## Installation

Führe folgende Schritte aus, um das Projekt auf deinem System einzurichten:

1. **Repository klonen**

   ```bash
   git clone https://github.com/dein-user/hvac-classifier.git
   cd hvac-classifier
   ```
2. **Virtuelle Umgebung erstellen und aktivieren**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. **Abhängigkeiten installieren**

   ```bash
   pip install -r requirements.txt
   ```
4. **Umgebungsvariablen konfigurieren**

   Erstelle eine `.env`-Datei im Hauptverzeichnis:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/hvacdb
   FLASK_APP=main.py
   FLASK_ENV=development
   ```

5. **Datenbank initialisieren**

   ```bash
   # PostgreSQL-Datenbank erstellen
   createdb hvacdb
   
   # Schema anwenden
   psql -d hvacdb -f hvacdb.sql
   ```

## Projektstruktur

```
hvac-classifier/
│
├── main.py                     # Hauptskript und Flask-Anwendung
├── config.py                   # Konfigurationseinstellungen
├── models.py                   # SQLAlchemy-Datenbankmodelle
├── hvacdb.sql                  # SQL-Schema für die Datenbank
│
├── classifier/                 # Klassifizierungsmodule
│   ├── hvac_rules.py           # Definition der Klassifizierungsregeln
│   ├── location_extractor.py   # Extraktion von Standortinformationen
│   ├── hvac_extractor.py       # Extraktion von HVAC-Komponenten
│   └── bas_converter.py        # Konvertierung zwischen BAS-Standards
│
├── samples/                    # Beispiel-IFC-Dateien
│   └── test_model.ifc          # Beispielhafte IFC-Datei
│
├── templates/                  # HTML-Templates
│   ├── index.html              # Hauptseite
│   ├── model_details.html      # Modelldetailansicht
│   └── component_details.html  # Komponentendetailansicht
│
├── static/                     # Statische Dateien
│   ├── style.css               # CSS-Styles
│   └── javascripts/            # JavaScript-Dateien
│       └── index.js            # Hauptscript für die Weboberfläche
│
├── uploads/                    # Verzeichnis für hochgeladene Dateien
├── venv/                       # Virtuelle Python-Umgebung (ignoriert)
├── requirements.txt            # Python-Abhängigkeiten
└── README.md                   # Diese Projektbeschreibung
```

## Erste Schritte

### 1. Testlauf in der Konsole

```bash
python main.py samples/test_model.ifc
```

Dies verarbeitet die Datei `samples/test_model.ifc` und gibt erkannte HVAC-Elemente in der Konsole aus.

### 2. Weboberfläche starten

```bash
python main.py
```

Öffne dann deinen Browser unter `http://127.0.0.1:5000`, um die Weboberfläche zu nutzen.

## Architektur

Das Projekt verwendet eine modulare Architektur mit folgenden Hauptkomponenten:

1. **LocationExtractor**: Extrahiert Standortinformationen (Stockwerk, Raum) aus IFC-Dateien.
2. **HVACExtractor**: Identifiziert HVAC-Komponenten und deren Eigenschaften in IFC-Dateien.
3. **HVACClassifier**: Klassifiziert HVAC-Komponenten nach BACTwin und AMEV-Standards.
4. **BASConverter**: Konvertiert zwischen verschiedenen BAS-Code-Standards.

Die Datenbank besteht aus folgenden Tabellen:
- `ifc_models`: Importierte IFC-Modelle
- `locations`: Standortinformationen (Stockwerk, Raum)
- `hvac_components`: HVAC-Komponenten mit Eigenschaften und Klassifizierung
- `distribution_systems`: Versorgungs- und Verteilungssysteme
- `classification_mappings`: Zuordnungen zwischen IFC-Klassen und Kategorien

Die Weboberfläche bietet:
- Upload und Verarbeitung von IFC-Dateien
- Ansicht als Baumstruktur oder Tabelle
- Detailansicht von Komponenten
- Filterung nach elektronisch gesteuerten Elementen
- Export von Klassifizierungsergebnissen

## Roadmap

* **Machine-Learning-Erweiterung**: Automatisierte Klassifizierung basierend auf neuronalen Netzen
* **Unterstützung zusätzlicher Formate**: Revit, ArchiCAD, .rvt, .pln
* **3D-Visualisierung**: Integration mit three.js oder xeokit
* **Testautomatisierung und CI/CD**: GitHub Actions für Qualitätssicherung
* **BACnet-Integration**: Anbindung an Gebäudeautomationssysteme

## Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE). Alle Beiträge sind willkommen — bitte befolge die geltenden Lizenzrichtlinien.