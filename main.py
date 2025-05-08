from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

from config import Config
from models import db, IFCModel, HVACComponent, DistributionSystem, ClassificationMapping
from classifier.hvac_extractor import extract_and_persist

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route("/", methods=["GET"])
def index():
    model = IFCModel.query.order_by(IFCModel.uploaded_at.desc()).first()
    components = model.components if model else []
    mappings = ClassificationMapping.query.all()
    return render_template("index.html", components=components, mappings=mappings)

@app.route("/upload", methods=["POST"])
def upload_model():
    file = request.files.get("ifc_file")
    if not file:
        return redirect(url_for("index"))
    filename = secure_filename(file.filename)
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    upload_path = os.path.join(upload_dir, filename)
    file.save(upload_path)
    model_record = IFCModel(filename=filename)
    db.session.add(model_record)
    db.session.commit()
    extract_and_persist(upload_path, model_record)
    return redirect(url_for("index"))

@app.route("/detail/<int:id>", methods=["GET", "POST"])
def component_detail(id):
    comp = HVACComponent.query.get_or_404(id)
    mappings = ClassificationMapping.query.all()
    if request.method == "POST":
        comp.mapping_id = request.form.get("mapping")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("detail.html", component=comp, mappings=mappings)

@app.route("/export", methods=["GET"])
def export():
    path = "export.csv"
    with open(path, "w") as f:
        f.write("Global ID,Name,IFC Class,System,Category\n")
        for comp in HVACComponent.query.all():
            f.write(f"{comp.global_id},{comp.name},{comp.ifc_class},{comp.system.name if comp.system else ''},{comp.mapping.target_category if comp.mapping else ''}\n")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

