# HVAC Classifier Prototype

**Prototyp zur automatischen Kategorisierung von HVAC-Komponenten in BIM-Modellen**

---

## 📋 Inhaltsverzeichnis

1. [Projektübersicht](#projektübersicht)
2. [Hauptfunktionen](#hauptfunktionen)
3. [Voraussetzungen](#voraussetzungen)
4. [Installation](#installation)
5. [Projektstruktur](#projektstruktur)
6. [Erste Schritte](#erste-schritte)
7. [Roadmap](#roadmap)
8. [Lizenz](#lizenz)

---

## Projektübersicht

In diesem Projekt wird ein Prototyp entwickelt, der **HVAC-Komponenten** (Heizung, Lüftung, Klima) in digitalen Bauwerksmodellen automatisch erkennt und gemäß den deutschen Standards **BACTwin** und **AMEV** kategorisiert. Durch die Automatisierung wird der manuelle Aufwand minimiert, Fehlerraten reduziert und eine einheitliche Klassifizierung sichergestellt.

## Hauptfunktionen

* **IFC-Import**: Einlesen und Verarbeiten von BIM-Modellen im IFC-Format
* **Erkennung**: Identifikation relevanter HVAC-Elemente (z. B. Luftauslässe, Heizkörper, Ventile)
* **Klassifizierung**: Zuordnung gemäß BACTwin- und AMEV-Standard
* **Ausgabeoptionen**: Ergebnisse wahlweise in der Konsole oder in einer Weboberfläche (Flask)

## Voraussetzungen

* **Python** 3.8 oder neuer
* **ifcopenshell** zum Parsen von IFC-Dateien
* **Flask** für das optionale Webfrontend

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

## Projektstruktur

```bash
hvac-classifier/
│
├── main.py                 # Hauptskript zum Einlesen und Klassifizieren
├── classifier/
│   └── hvac_rules.py       # Definition der Klassifizierungsregeln
├── samples/
│   └── test_model.ifc      # Beispielhafte IFC-Datei
├── templates/
│   └── index.html          # HTML-Template für das Flask-Frontend
├── static/
│   └── style.css           # CSS-Datei für die Weboberfläche
├── requirements.txt        # Python-Abhängigkeiten
└── README.md               # Diese Projektbeschreibung
```

## Erste Schritte

### 1. Testlauf in der Konsole

```bash
python main.py
```

Dies lädt die Datei `samples/test_model.ifc` und gibt erkannte HVAC-Elemente in der Konsole aus.

### 2. Weboberfläche starten

```bash
export FLASK_APP=main.py  # macOS/Linux
set FLASK_APP=main.py     # Windows
flask run
```

Öffne dann deinen Browser unter `http://127.0.0.1:5000`, um das Ergebnis grafisch zu betrachten.

## Roadmap

* **Machine-Learning-Erweiterung**: Automatisierte Klassifizierung basierend auf neuronalen Netzen
* **Unterstützung zusätzlicher Formate**: Revit, ArchiCAD, .rvt, .pln
* **3D-Visualisierung**: Integration mit three.js oder xeokit
* **Testautomatisierung und CI/CD**: GitHub Actions für Qualitätssicherung

## Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE). Alle Beiträge sind willkommen — bitte befolge die geltenden Lizenzrichtlinien.
