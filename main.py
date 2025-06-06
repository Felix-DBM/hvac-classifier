"""
Angepasste Hauptanwendung (main.py) mit Integration aller Komponenten
"""

import os
import sys
import json
import ifcopenshell
from flask import Flask, request, render_template, jsonify, send_from_directory, flash, redirect, url_for, Response, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_migrate import Migrate
from flask_session import Session

# Import der eigenen Module
from models import db, IFCModel, HVACComponent, Location, ClassificationMapping, DistributionSystem
from classifier.location_extractor import LocationExtractor
from classifier.hvac_rules import HVACClassifier
from classifier.hvac_extractor import HVACExtractor
from classifier.bas_converter import BASConverter

# Konfiguration
from config import Config

# Absolute Pfade zu den Verzeichnissen
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web_interface', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'web_interface', 'static'))

# Flask-App mit absoluten Pfaden initialisieren
app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)
app.config.from_object(Config)
app.secret_key = "hvac-classifier-secret-key"  # Für Flash-Nachrichten

# Session-Konfiguration für PostgreSQL
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db  # Deine SQLAlchemy-Datenbank-Instanz
app.config['SESSION_SQLALCHEMY_TABLE'] = 'flask_sessions'  # Name der Tabelle in PostgreSQL
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session hält eine Woche
app.config['SESSION_USE_SIGNER'] = True  # Signiere die Session-Cookie-Daten
app.config['SESSION_KEY_PREFIX'] = 'hvac_'  # Präfix für Session-Schlüssel

# Datenbank initialisieren
db.init_app(app)
migrate = Migrate(app, db)

# Session initialisieren (nach db.init_app!)
Session(app)

# Verzeichnisse
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
SAMPLES_FOLDER = os.path.join(app.root_path, 'samples')

# Stelle sicher, dass die benötigten Verzeichnisse existieren
for directory in [UPLOAD_FOLDER, SAMPLES_FOLDER]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Erlaubte Dateierweiterungen
ALLOWED_EXTENSIONS = {'ifc'}

def allowed_file(filename):
    """Prüft, ob die Dateierweiterung erlaubt ist"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Hauptseite der Anwendung"""
    # Statistiken abrufen
    statistics = get_statistics()
    
    # Lade alle Beispieldateien
    samples = get_sample_files()
    
    # Lade Sitzungsdateien
    session_files = get_session_files()
    
    return render_template('index.html', 
                          statistics=statistics, 
                          samples=samples, 
                          session_files=session_files,
                          page_title="Dashboard")

@app.route('/upload', methods=['POST'])
def upload_file():
    """Verarbeitet eine hochgeladene IFC-Datei"""
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Keine Datei ausgewählt', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Standard
        standard = request.form.get('standard', 'amev')
        electronic_only = request.form.get('electronic_only', 'true').lower() == 'true'
        
        # Verarbeite die Datei
        try:
            model_id = process_ifc_file(filepath, filename, standard, electronic_only)
            flash(f'Datei "{filename}" erfolgreich verarbeitet', 'success')
            return redirect(url_for('view_model', model_id=model_id))
        except Exception as e:
            flash(f'Fehler bei der Verarbeitung: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        flash('Nicht erlaubter Dateityp. Nur IFC-Dateien sind erlaubt.', 'error')
        return redirect(request.url)
    
@app.route('/debug/session')
def debug_session():
    """Nur für Debugging: Zeigt den Inhalt der aktuellen Session an"""
    if app.debug:
        session_info = {
            'session_data': dict(session),
            'processed_files': session.get('processed_files', [])
        }
        return jsonify(session_info)
    else:
        return "Debugging ist deaktiviert", 403

@app.route('/api/upload', methods=['POST'])
def api_upload_file():
    """API-Endpunkt für das Hochladen und Verarbeiten einer IFC-Datei"""
    if 'file' not in request.files:
        return jsonify({'error': 'Keine Datei hochgeladen'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Standard
        standard = request.form.get('standard', 'amev')
        electronic_only = request.form.get('electronic_only', 'true').lower() == 'true'
        
        # Verarbeite die Datei
        try:
            model_id = process_ifc_file(filepath, filename, standard, electronic_only)
            
            # Lade das verarbeitete Modell mit seinen Komponenten
            model = IFCModel.query.get(model_id)
            components = HVACComponent.query.filter_by(model_id=model_id).all()
            
            # Hierarchische Struktur erstellen
            hierarchy = create_hierarchy_from_components(components)
            
            # Ergebnisse zurückgeben
            return jsonify({
                'model_id': model_id,
                'filename': model.filename,
                'uploaded_at': model.uploaded_at.isoformat(),
                'component_count': len(components),
                'flat_results': [component.to_dict() for component in components],
                'hierarchy': hierarchy
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Nicht erlaubter Dateityp. Nur IFC-Dateien sind erlaubt.'}), 400

@app.route('/model/<int:model_id>')
def view_model(model_id):
    """Zeigt Details eines verarbeiteten Modells an"""
    model = IFCModel.query.get_or_404(model_id)
    components = HVACComponent.query.filter_by(model_id=model_id).all()
    
    # Systeme für Filter
    systems = DistributionSystem.query.all()
    
    # Zähler für elektronische Komponenten
    electronic_count = sum(1 for c in components if c.is_electronic)
    
    return render_template(
        'model_details.html',
        model=model,
        components=components,
        systems=systems,
        electronic_count=electronic_count
    )

@app.route('/export/model/<int:model_id>')
def export_model_data(model_id):
    """Exportiert Modelldaten in verschiedenen Formaten"""
    format_type = request.args.get('format', 'csv')
    include_properties = request.args.get('properties', 'true').lower() == 'true'
    include_location = request.args.get('location', 'true').lower() == 'true'
    filtered_only = request.args.get('filtered', 'false').lower() == 'true'
    
    # Lade das Modell
    model = IFCModel.query.get_or_404(model_id)
    
    # Lade die Komponenten
    components = HVACComponent.query.filter_by(model_id=model_id).all()
    
    # Formatspezifische Exportlogik
    if format_type == 'csv':
        return export_csv(model, components, include_properties, include_location)
    elif format_type == 'json':
        return export_json(model, components, include_properties, include_location)
    elif format_type == 'xlsx':
        return export_excel(model, components, include_properties, include_location)
    else:
        flash('Unbekanntes Exportformat.', 'error')
        return redirect(url_for('view_model', model_id=model_id))

@app.route('/api/model/<int:model_id>')
def api_model_data(model_id):
    """API-Endpunkt für Modelldaten"""
    model = IFCModel.query.get_or_404(model_id)
    components = HVACComponent.query.filter_by(model_id=model_id).all()
    
    # Filter anwenden
    electronic_only = request.args.get('electronic_only', 'false').lower() == 'true'
    if electronic_only:
        components = [c for c in components if c.is_electronic]
    
    system_id = request.args.get('system_id')
    if system_id and system_id.isdigit():
        components = [c for c in components if c.system_id == int(system_id)]
    
    # Hierarchische Struktur erstellen
    hierarchy = create_hierarchy_from_components(components)
    
    return jsonify({
        'model_id': model.id,
        'filename': model.filename,
        'uploaded_at': model.uploaded_at.isoformat(),
        'component_count': len(components),
        'flat_results': [component.to_dict() for component in components],
        'hierarchy': hierarchy
    })

@app.route('/api/convert', methods=['POST'])
def convert_bas_code():
    """Konvertiert einen BAS-Code zwischen Standards"""
    data = request.json
    if not data or 'code' not in data or 'from_standard' not in data or 'to_standard' not in data:
        return jsonify({'error': 'Fehlende Parameter'}), 400
    
    code = data['code']
    from_standard = data['from_standard'].lower()
    to_standard = data['to_standard'].lower()
    
    converter = BASConverter()
    
    try:
        if from_standard == 'vdi' and to_standard == 'amev':
            result = converter.convert_vdi_to_amev(code)
        elif from_standard == 'amev' and to_standard == 'vdi':
            result = converter.convert_amev_to_vdi(code)
        else:
            return jsonify({'error': 'Ungültige Standards'}), 400
        
        return jsonify({
            'original_code': code,
            'converted_code': result,
            'from_standard': from_standard,
            'to_standard': to_standard
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/component/<int:component_id>')
def view_component(component_id):
    """Zeigt Details einer Komponente an"""
    component = HVACComponent.query.get_or_404(component_id)
    return render_template('component_details.html', component=component)

@app.route('/api/component/<int:component_id>')
def api_component_data(component_id):
    """API-Endpunkt für Komponentendaten"""
    component = HVACComponent.query.get_or_404(component_id)
    return jsonify(component.to_dict())

@app.route('/samples')
def list_samples():
    """Listet verfügbare Beispieldateien auf"""
    samples = []
    for filename in os.listdir(SAMPLES_FOLDER):
        if filename.endswith('.ifc'):
            filepath = os.path.join(SAMPLES_FOLDER, filename)
            filesize = os.path.getsize(filepath)
            samples.append({
                'filename': filename,
                'filesize': format_filesize(filesize),
                'path': url_for('download_sample', filename=filename)
            })
    return render_template('samples.html', samples=samples)

@app.route('/samples/<filename>')
def download_sample(filename):
    """Stellt eine Beispieldatei zum Download bereit"""
    return send_from_directory(SAMPLES_FOLDER, filename)

@app.route('/api/statistics')
def api_statistics():
    """Liefert statistische Daten zur Anwendung"""
    models_count = IFCModel.query.count()
    components_count = HVACComponent.query.count()
    electronic_count = HVACComponent.query.filter_by(is_electronic=True).count()
    
    # Komponenten nach Klasse
    component_classes = db.session.query(
        HVACComponent.ifc_class, 
        db.func.count(HVACComponent.id)
    ).group_by(HVACComponent.ifc_class).all()
    
    class_stats = {cls: count for cls, count in component_classes}
    
    return jsonify({
        'models_count': models_count,
        'components_count': components_count,
        'electronic_count': electronic_count,
        'electronic_percentage': round(electronic_count / components_count * 100, 1) if components_count else 0,
        'class_distribution': class_stats
    })

def process_ifc_file(filepath, filename, standard="amev", electronic_only=True, overwrite_mode="update"):
    """
    Verarbeitet eine IFC-Datei und speichert die Ergebnisse in der Datenbank
    mit UPSERT-Logik (Aktualisieren, wenn der Eintrag bereits existiert)
    
    Args:
        filepath: Pfad zur IFC-Datei
        filename: Name der Datei
        standard: BAS-Standard (amev oder vdi)
        electronic_only: Nur elektronisch gesteuerte Elemente berücksichtigen
        overwrite_mode: "update" (aktualisieren), "replace" (ersetzen) oder "skip" (überspringen)
        
    Returns:
        int: ID des erstellten Modells
    """
    # IFC-Datei öffnen
    ifc_file = ifcopenshell.open(filepath)
    
    # Modell in Datenbank erstellen oder aktualisieren
    existing_model = IFCModel.query.filter_by(filename=filename).first()
    
    if existing_model:
        if overwrite_mode == "replace":
            # Lösche alle bestehenden Komponenten dieses Modells
            components_to_delete = HVACComponent.query.filter_by(model_id=existing_model.id).all()
            
            for component in components_to_delete:
                # Lösche auch zugehörige Standorte
                if component.location_id:
                    location = Location.query.get(component.location_id)
                    if location:
                        db.session.delete(location)
                db.session.delete(component)
                
            # Nutze das bestehende Modell
            model = existing_model
        elif overwrite_mode == "skip":
            # Verwende einfach das bestehende Modell ohne Änderungen
            return existing_model.id
        else:  # "update" ist der Standard
            # Nutze das bestehende Modell und aktualisiere Komponenten
            model = existing_model
    else:
        # Neues Modell erstellen
        model = IFCModel(filename=filename)
        db.session.add(model)
        db.session.flush()  # ID generieren
    
    # Extraktoren und Classifier initialisieren
    location_extractor = LocationExtractor(ifc_file)
    hvac_extractor = HVACExtractor(ifc_file)
    hvac_classifier = HVACClassifier(ifc_file, location_extractor)
    
    # HVAC-Elemente klassifizieren
    classification_results = hvac_classifier.classify_all_hvac_elements(standard, electronic_only)
    
    # Iteriere durch klassifizierte Elemente
    for element_data in classification_results["flat_results"]:
        # Global ID ermitteln
        global_id = element_data.get("metadata", {}).get("global_id", f"ID_{element_data['element_id']}")
        
        # Prüfen, ob Komponente bereits existiert
        existing_component = HVACComponent.query.filter_by(global_id=global_id, model_id=model.id).first()
        
        # Standort verarbeiten
        location_id = None
        if "location" in element_data:
            location_data = element_data["location"]
            # Standort suchen oder erstellen
            if existing_component and existing_component.location_id and overwrite_mode == "update":
                # Bestehenden Standort aktualisieren
                location = Location.query.get(existing_component.location_id)
                if location:
                    location.storey_id = location_data.get("storey_id")
                    location.storey_name = location_data.get("storey_name")
                    location.space_id = location_data.get("space_id")
                    location.space_name = location_data.get("space_name")
                    location_id = location.id
                else:
                    # Standort nicht gefunden, neuen erstellen
                    location = Location(
                        storey_id=location_data.get("storey_id"),
                        storey_name=location_data.get("storey_name"),
                        space_id=location_data.get("space_id"),
                        space_name=location_data.get("space_name")
                    )
                    db.session.add(location)
                    db.session.flush()
                    location_id = location.id
            else:
                # Neuen Standort erstellen
                location = Location(
                    storey_id=location_data.get("storey_id"),
                    storey_name=location_data.get("storey_name"),
                    space_id=location_data.get("space_id"),
                    space_name=location_data.get("space_name")
                )
                db.session.add(location)
                db.session.flush()
                location_id = location.id
        
        # Komponente aktualisieren oder erstellen
        if existing_component and overwrite_mode == "update":
            # Komponente aktualisieren
            existing_component.name = element_data["element_name"]
            existing_component.ifc_class = element_data["element_type"]
            existing_component.is_electronic = element_data["is_electronic"]
            existing_component.bas_code = element_data["bas_code"]
            existing_component.bas_standard = standard
            existing_component.properties = element_data.get("properties", {})
            existing_component.location_id = location_id
        else:
            # Neue Komponente erstellen
            component = HVACComponent(
                global_id=global_id,
                name=element_data["element_name"],
                ifc_class=element_data["element_type"],
                is_electronic=element_data["is_electronic"],
                bas_code=element_data["bas_code"],
                bas_standard=standard,
                properties=element_data.get("properties", {}),
                model_id=model.id,
                location_id=location_id
            )
            db.session.add(component)
    
    # Änderungen speichern
    db.session.commit()
    return model.id

def create_hierarchy_from_components(components):
    """
    Erstellt eine hierarchische Struktur aus den Komponenten nach Standort
    
    Args:
        components: Liste von HVACComponent-Objekten
        
    Returns:
        dict: Hierarchische Struktur nach Stockwerk und Raum
    """
    hierarchy = {}
    
    for component in components:
        if not component.location:
            # Komponenten ohne Standortinformation unter "Unbekannter Standort" sammeln
            storey_name = "Unbekannter Standort"
            if storey_name not in hierarchy:
                hierarchy[storey_name] = {
                    "id": None,
                    "name": storey_name,
                    "type": "storey",
                    "children": {}
                }
            
            # Komponente direkt dem Stockwerk hinzufügen
            element_id = str(component.id)
            hierarchy[storey_name]["children"][element_id] = {
                "id": component.id,
                "name": component.name,
                "type": component.ifc_class,
                "bas_code": component.bas_code,
                "is_electronic": component.is_electronic
            }
            continue
        
        # Stockwerksinformationen
        storey_name = component.location.storey_name
        storey_id = component.location.storey_id
        
        # Stockwerk hinzufügen, falls noch nicht vorhanden
        if storey_name not in hierarchy:
            hierarchy[storey_name] = {
                "id": storey_id,
                "name": storey_name,
                "type": "storey",
                "children": {}
            }
        
        # Rauminformationen
        space_name = component.location.space_name
        space_id = component.location.space_id
        
        # Wenn Raum vorhanden, Komponente zum Raum hinzufügen
        if space_name:
            # Raum hinzufügen, falls noch nicht vorhanden
            if space_name not in hierarchy[storey_name]["children"]:
                hierarchy[storey_name]["children"][space_name] = {
                    "id": space_id,
                    "name": space_name,
                    "type": "space",
                    "children": {}
                }
            
            # Komponente dem Raum hinzufügen
            element_id = str(component.id)
            hierarchy[storey_name]["children"][space_name]["children"][element_id] = {
                "id": component.id,
                "name": component.name,
                "type": component.ifc_class,
                "bas_code": component.bas_code,
                "is_electronic": component.is_electronic
            }
        else:
            # Komponente direkt dem Stockwerk hinzufügen, wenn kein Raum vorhanden
            element_id = str(component.id)
            hierarchy[storey_name]["children"][element_id] = {
                "id": component.id,
                "name": component.name,
                "type": component.ifc_class,
                "bas_code": component.bas_code,
                "is_electronic": component.is_electronic
            }
    
    return hierarchy

def format_filesize(size_bytes):
    """Formatiert eine Dateigröße in Bytes in ein lesbares Format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_statistics():
    """Sammelt Statistiken für das Dashboard"""
    models_count = IFCModel.query.count()
    components_count = HVACComponent.query.count()
    electronic_count = HVACComponent.query.filter_by(is_electronic=True).count()
    
    # Komponenten nach Klasse
    component_classes = db.session.query(
        HVACComponent.ifc_class, 
        db.func.count(HVACComponent.id)
    ).group_by(HVACComponent.ifc_class).all()
    
    class_stats = {cls: count for cls, count in component_classes}
    
    # Häufigste Klasse ermitteln
    most_common_class = None
    most_common_count = 0
    for cls, count in component_classes:
        if count > most_common_count:
            most_common_count = count
            most_common_class = cls
    
    return {
        'models_count': models_count,
        'components_count': components_count,
        'electronic_count': electronic_count,
        'electronic_percentage': round(electronic_count / components_count * 100, 1) if components_count else 0,
        'class_distribution': class_stats,
        'most_common_class': most_common_class,
        'most_common_count': most_common_count
    }

def get_sample_files():
    """Sammelt verfügbare Beispieldateien"""
    samples = []
    if os.path.exists(SAMPLES_FOLDER):
        for filename in os.listdir(SAMPLES_FOLDER):
            if filename.endswith('.ifc'):
                filepath = os.path.join(SAMPLES_FOLDER, filename)
                filesize = os.path.getsize(filepath)
                samples.append({
                    'filename': filename,
                    'filesize': format_filesize(filesize),
                    'path': url_for('download_sample', filename=filename)
                })
    return samples

def add_file_to_session(model_id):
    """Fügt eine verarbeitete Datei zur aktuellen Sitzung hinzu"""
    if 'processed_files' not in session:
        session['processed_files'] = []
    
    # Prüfe, ob die Datei bereits in der Sitzung ist
    for file_info in session['processed_files']:
        if file_info['id'] == model_id:
            # Datei bereits vorhanden, aktualisiere Zeitpunkt
            file_info['processed_at'] = datetime.now().strftime('%d.%m.%Y, %H:%M')
            session.modified = True
            return
    
    # Lade Modellinformationen
    model = IFCModel.query.get(model_id)
    components = HVACComponent.query.filter_by(model_id=model_id).all()
    electronic_count = sum(1 for c in components if c.is_electronic)
    
    # Neue Datei zur Sitzung hinzufügen
    file_info = {
        'id': model_id,
        'filename': model.filename,
        'processed_at': datetime.now().strftime('%d.%m.%Y, %H:%M'),
        'component_count': len(components),
        'electronic_count': electronic_count,
        'standard': components[0].bas_standard if components else 'amev'
    }
    
    session['processed_files'].insert(0, file_info)  # Am Anfang einfügen
    
    # Begrenze die Anzahl der gespeicherten Dateien
    if len(session['processed_files']) > 10:
        session['processed_files'] = session['processed_files'][:10]
    
    session.modified = True
    session.permanent = True

def get_session_files():
    """Gibt die Dateien der aktuellen Sitzung zurück"""
    if 'processed_files' not in session:
        return []
    
    # Überprüfe, ob alle Modelle noch in der Datenbank sind
    valid_files = []
    for file_info in session['processed_files']:
        model = IFCModel.query.get(file_info['id'])
        if model:
            valid_files.append(file_info)
    
    # Aktualisiere die Session, falls einige Modelle nicht mehr existieren
    if len(valid_files) != len(session['processed_files']):
        session['processed_files'] = valid_files
        session.modified = True
    
    return valid_files

def export_csv(model, components, include_properties, include_location):
    """Exportiert Modelldaten als CSV"""
    import csv
    from io import StringIO
    
    # CSV-Datei im Speicher erstellen
    csv_data = StringIO()
    fieldnames = ['id', 'global_id', 'name', 'ifc_class', 'is_electronic', 'bas_code', 'bas_standard']
    
    # Füge Standortfelder hinzu, wenn gewünscht
    if include_location:
        fieldnames.extend(['storey_name', 'space_name'])
    
    # Füge Eigenschaftsfelder hinzu, wenn gewünscht
    if include_properties:
        fieldnames.append('properties')
    
    writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
    writer.writeheader()
    
    # Füge Komponenten hinzu
    for component in components:
        row = {
            'id': component.id,
            'global_id': component.global_id,
            'name': component.name,
            'ifc_class': component.ifc_class,
            'is_electronic': component.is_electronic,
            'bas_code': component.bas_code,
            'bas_standard': component.bas_standard
        }
        
        # Füge Standortinformationen hinzu
        if include_location and component.location:
            row['storey_name'] = component.location.storey_name
            row['space_name'] = component.location.space_name
        
        # Füge Eigenschaften hinzu
        if include_properties:
            row['properties'] = json.dumps(component.properties)
        
        writer.writerow(row)
    
    # Response erstellen
    csv_data.seek(0)
    
    # Erstelle Dateinamen
    filename = f"{model.filename.rsplit('.', 1)[0]}_export.csv"
    
    return Response(
        csv_data.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

def export_json(model, components, include_properties, include_location):
    """Exportiert Modelldaten als JSON"""
    result = {
        "model": {
            "id": model.id,
            "filename": model.filename,
            "uploaded_at": model.uploaded_at.isoformat()
        },
        "components": []
    }
    
    # Komponenten hinzufügen
    for component in components:
        comp_data = {
            "id": component.id,
            "global_id": component.global_id,
            "name": component.name,
            "ifc_class": component.ifc_class,
            "is_electronic": component.is_electronic,
            "bas_code": component.bas_code,
            "bas_standard": component.bas_standard
        }
        
        # Standortinformationen hinzufügen
        if include_location and component.location:
            comp_data["location"] = {
                "storey_name": component.location.storey_name,
                "storey_id": component.location.storey_id,
                "space_name": component.location.space_name,
                "space_id": component.location.space_id
            }
        
        # Eigenschaften hinzufügen
        if include_properties:
            comp_data["properties"] = component.properties
        
        result["components"].append(comp_data)
    
    # Erstelle Dateinamen
    filename = f"{model.filename.rsplit('.', 1)[0]}_export.json"
    
    return Response(
        json.dumps(result, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

def export_excel(model, components, include_properties, include_location):
    """Exportiert Modelldaten als Excel-Datei"""
    # Hier benötigst du eine Excel-Bibliothek wie xlsxwriter oder openpyxl
    # Dies ist nur ein Beispiel mit openpyxl
    try:
        from openpyxl import Workbook
        from io import BytesIO
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Komponenten"
        
        # Header hinzufügen
        headers = ['ID', 'Global ID', 'Name', 'IFC-Klasse', 'Elektronisch', 'BAS-Code', 'BAS-Standard']
        
        # Füge Standortfelder hinzu
        if include_location:
            headers.extend(['Stockwerk', 'Raum'])
        
        # Eigenschaften-Header
        if include_properties:
            headers.append('Eigenschaften')
        
        ws.append(headers)
        
        # Daten hinzufügen
        for component in components:
            row = [
                component.id,
                component.global_id,
                component.name,
                component.ifc_class,
                'Ja' if component.is_electronic else 'Nein',
                component.bas_code,
                component.bas_standard
            ]
            
            # Standortinformationen
            if include_location:
                if component.location:
                    row.extend([
                        component.location.storey_name,
                        component.location.space_name
                    ])
                else:
                    row.extend(['', ''])
            
            # Eigenschaften
            if include_properties:
                row.append(json.dumps(component.properties))
            
            ws.append(row)
        
        # Spaltenbreiten anpassen
        for i, column in enumerate(ws.columns, 1):
            max_length = 0
            column_letter = ws.cell(row=1, column=i).column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            
            adjusted_width = max(10, min(max_length + 2, 50))
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Speichere in BytesIO
        excel_data = BytesIO()
        wb.save(excel_data)
        excel_data.seek(0)
        
        # Erstelle Dateinamen
        filename = f"{model.filename.rsplit('.', 1)[0]}_export.xlsx"
        
        return Response(
            excel_data.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    
    except ImportError:
        flash('Excel-Export benötigt die openpyxl-Bibliothek, die nicht installiert ist.', 'error')
        return redirect(url_for('view_model', model_id=model.id))

# Hauptprogramm
if __name__ == '__main__':
    with app.app_context():
        # Datenbank initialisieren
        db.create_all()
    
    if len(sys.argv) > 1:
        # Ausführung als Kommandozeilenprogramm
        ifc_file_path = sys.argv[1]
        output_format = sys.argv[2] if len(sys.argv) > 2 else "console"
        standard = sys.argv[3] if len(sys.argv) > 3 else "amev"
        electronic_only = sys.argv[4].lower() == "true" if len(sys.argv) > 4 else True
        
        # IFC-Datei öffnen
        ifc_file = ifcopenshell.open(ifc_file_path)
        
        # Extraktoren und Classifier initialisieren
        location_extractor = LocationExtractor(ifc_file)
        hvac_classifier = HVACClassifier(ifc_file, location_extractor)
        
        # HVAC-Elemente klassifizieren
        results = hvac_classifier.classify_all_hvac_elements(standard, electronic_only)
        
        # Ausgabe
        if output_format == "console":
            print(f"Ergebnisse für {ifc_file_path}:")
            print(f"Standard: {standard}")
            print(f"Nur elektronisch gesteuerte Elemente: {electronic_only}")
            print("-" * 80)
            
            # Flache Liste ausgeben
            for i, element in enumerate(results["flat_results"]):
                print(f"Element {i+1}:")
                print(f"  Name: {element['element_name']}")
                print(f"  Typ: {element['element_type']}")
                print(f"  BAS-Code: {element['bas_code']}")
                if "location" in element:
                    loc = element["location"]
                    print(f"  Standort: {loc.get('storey_name', 'Unbekannt')}, {loc.get('space_name', 'Unbekannt')}")
                print(f"  Elektronisch gesteuert: {element['is_electronic']}")
                print()
                
        elif output_format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # Ausführung als Webanwendung
        print("HVAC Classifier Webinterface wird gestartet...")
        print("Öffnen Sie Ihren Browser unter http://127.0.0.1:5000")
        print("Laden Sie eine IFC-Datei hoch, um HVAC-Elemente zu klassifizieren.")
        print("-" * 80)
        print("Hinweis: Stellen Sie sicher, dass Sie eine gültige IFC-Datei verwenden.")
        print("Das Programm extrahiert Standortinformationen (Stockwerk, Raum) aus der IFC-Datei")
        print("und integriert diese in den generierten BAS-Code.")
        
        app.run(debug=True, host='0.0.0.0', port=5000)