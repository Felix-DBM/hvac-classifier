from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class IFCModel(db.Model):
    __tablename__ = "ifc_models"

    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String,  nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Beziehung zu HVACComponent
    components  = db.relationship(
        "HVACComponent",
        back_populates="model",
        cascade="all, delete-orphan"
    )

class DistributionSystem(db.Model):
    __tablename__ = "distribution_systems"

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String,  nullable=False)
    predefined_type= db.Column(db.String)

    # Beziehung zu HVACComponent
    components     = db.relationship(
        "HVACComponent",
        back_populates="system",
        cascade="all, delete-orphan"
    )

class ClassificationMapping(db.Model):
    __tablename__ = "classification_mappings"

    id              = db.Column(db.Integer, primary_key=True)
    ifc_class       = db.Column(db.String,  nullable=False)
    predefined_type = db.Column(db.String)
    target_category = db.Column(db.String,  nullable=False)
    bac_twin_code   = db.Column(db.String)
    amev_code       = db.Column(db.String)

    # Beziehung zu HVACComponent
    components      = db.relationship(
        "HVACComponent",
        back_populates="mapping"
    )

class HVACComponent(db.Model):
    __tablename__ = "hvac_components"

    id          = db.Column(db.Integer, db.ForeignKey("ifc_models.id"), primary_key=True)
    global_id   = db.Column(db.String, unique=True, nullable=False)
    name        = db.Column(db.String)
    ifc_class   = db.Column(db.String, nullable=False)
    object_type = db.Column(db.String)
    properties  = db.Column(db.JSON)

    model_id    = db.Column(db.Integer, db.ForeignKey("ifc_models.id"))
    system_id   = db.Column(db.Integer, db.ForeignKey("distribution_systems.id"))
    mapping_id  = db.Column(db.Integer, db.ForeignKey("classification_mappings.id"))

    # Relationships
    model       = db.relationship(
        "IFCModel",
        back_populates="components"
    )
    system      = db.relationship(
        "DistributionSystem",
        back_populates="components"
    )
    mapping     = db.relationship(
        "ClassificationMapping",
        back_populates="components"
    )
