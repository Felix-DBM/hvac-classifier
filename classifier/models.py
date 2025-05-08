from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class IFCModel(db.Model):
    __tablename__ = "ifc_models"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    components = db.relationship("HVACComponent", back_populates="model")

class DistributionSystem(db.Model):
    __tablename__ = "distribution_systems"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    predefined_type = db.Column(db.String)
    components = db.relationship("HVACComponent", back_populates="system")

class HVACComponent(db.Model):
    __tablename__ = "hvac_components"
    id = db.Column(db.Integer, primary_key=True)
    global_id = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    ifc_class = db.Column(db.String, nullable=False)
    object_type = db.Column(db.String)
    properties = db.Column(db.JSON)
    model_id = db.Column(db.Integer, db.ForeignKey("ifc_models.id"))
    system_id = db.Column(db.Integer, db.ForeignKey("distribution_systems.id"))
    model = db.relationship("IFCModel", back_populates="components")
    system = db.relationship("DistributionSystem", back_populates="components")

class ClassificationMapping(db.Model):
    __tablename__ = "classification_mappings"
    id = db.Column(db.Integer, primary_key=True)
    ifc_class = db.Column(db.String, nullable=False)
    predefined_type = db.Column(db.String)
    target_category = db.Column(db.String, nullable=False)
    bac_twin_code = db.Column(db.String)
    amev_code = db.Column(db.String)
