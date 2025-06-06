# HVAC Classifier

**Webbasierter Prototyp zur automatisierten Kategorisierung von HVAC-Komponenten in BIM-Modellen (IFC)**

---

## 📋 Inhaltsverzeichnis

1. [Projektübersicht](#projektübersicht)
2. [Hauptfunktionen](#hauptfunktionen)
3. [Voraussetzungen](#voraussetzungen)
4. [Installation](#installation)
5. [Projektübersicht](#projektübersicht)
6. [Programm starten](#programm-starten)
7. [Erste Schritte](#erste-schritte)
8. [Architektur](#architektur)
9. [Roadmap](#roadmap)
10. [Lizenz](#lizenz)

---

## Projektübersicht

HVAC Classifier ist ein auf Flask basierender Webprototyp zur **automatischen Klassifikation von Komponenten der technischen Gebäudeausrüstung (TGA)** in BIM-Modellen (IFC). Ziel ist es, die manuelle Zuordnung gemäß **BACTwin** und **AMEV**-Standards zu automatisieren, um die Datenqualität in digitalen Zwillingen zu erhöhen.

---

## Hauptfunktionen

- 🔍 **IFC-Import**: Verarbeitung und Visualisierung von BIM-Modellen im IFC-Format
- 🧠 **Klassifikation**: Regelbasierte Zuordnung von HVAC-Komponenten gemäß BAS-Standards
- 📌 **Positionsanalyse**: Raum- und Standorterkennung auf Basis von IFC-Geometrie
- 🌐 **Webinterface**: Benutzerfreundliche Oberfläche für Upload, Kontrolle und Export
- 🗃️ **Datenbank**: Speicherung aller Ergebnisse (SQLAlchemy, SQLite/PostgreSQL)
- 🧾 **Export**: Ergebnisse als Excel oder JSON-Datei verfügbar

---

## Voraussetzungen

- Python 3.10 oder 3.11
- pip / venv
- Abhängigkeiten aus `requirements.txt`

---

## Installation


Projekt klonen
```bash
git clone https://github.com/Awoladi/hvac-classifier
```
In der Ordnerstruktur in den hvac-classivier wechseln
```bash
cd hvac-classifier
```
Virtuelle Umgebung erstellen und aktivieren
```bash
python -m venv venv
source venv/bin/activate  # oder venv\Scripts\activate auf Windows
```
Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```
Datenbankverwaltung öffnen
```bash
psql -U postgres
```
#sollte bei Windows eine Warnugn wegen des Console code page kommen, dann kann die Datenbankverwaltung mit "\q" verlassen werden und mit "chcp 1252" geändert werden, wobei die Zahl das page angibt und geändert werden kann.

Datenbank erstellen und verwalten
```bash
#Datenbank über Datenbankverwaltung erstellen
CREATE DATABASE hvacdb;

#User in Datenbankwerwaltung erstellen
CREATE USER hvac_user WITH PASSWORD 'unser Passwort'; #unser Passwort sollte 'M31052003w' sein

#Berechtigungen in der Datenbankverwaltung für die Datenbank erteilen 
GRANT ALL PRIVILEGES ON DATABASE hvacdb TO hvac_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO hvac_user;
```
```bash
# Datenbank initialisieren/upgraden
flask db upgrade
```
---

## Programm starten
#Beachte, dass das virtuelle Environment gestartet sein muss
```bash
flask --app main run
```
---

## Projektstruktur

```text
├── main.py                   # Einstiegspunkt, Flask-Server  
├── config.py                 # Konfigurationen  
├── models.py                 # SQLAlchemy-Datenbankmodelle  
├── classifier/               # HVAC Klassifikationslogik  
│   ├── hvac_rules.py         # Regelbasierte Zuordnung  
│   ├── hvac_extractor.py     # IFC-Elementextraktion  
│   ├── location_extractor.py # Raum- und Bereichserkennung  
│   └── bas_converter.py      # Export in BAS-Formate  
├── web_interface/            # HTML-Templates und Static Files  
├── uploads/                  # Benutzeruploads  
├── samples/                  # Beispiel-IFC-Dateien  
├── hvacdb.sql                # Beispieldatenbank (optional)  
├── requirements.txt          # Python-Abhängigkeiten  
└── README.md                 # Diese Datei  
```

---

# Erste Schritte
1. Starte den Server:
   python main.py
2. Öffne http://localhost:5000 im Browser
3. Lade ein IFC-Modell hoch, klassifiziere HVAC-Elemente und exportiere das Ergebnis.

---

# Architektur
- Flask als leichtgewichtiges Webframework
- ifcopenshell zur Verarbeitung von IFC-Daten
- SQLAlchemy als ORM für relationale Speicherung
- Jinja2 Templates für Web-UI
- Regelbasierte Klassifikation via JSON-Regelsätze

---

# Roadmap
 - Modell-gestützte Klassifikation (ML)
 - Mehrsprachigkeit (DE/EN)
 - Unterstützung weiterer IFC-Versionen
 - Cloud-Upload-Optionen

---

# Lizenz 
Dieses Projekt steht unter MIT-Lizenz. Details siehe LICENSE-Datei.
