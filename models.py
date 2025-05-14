"""
Erweiterte models.py mit Integration für BAS-Codes und Standortinformationen
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class IFCModel(db.Model):
    __tablename__ = "ifc_models"

    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String,  nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    components  = db.relationship(
        "HVACComponent",
        back_populates="model",
        foreign_keys="[HVACComponent.model_id]"
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

class Location(db.Model):
    """Standortinformationen für HVAC-Komponenten"""
    __tablename__ = "locations"
    
    id          = db.Column(db.Integer, primary_key=True)
    storey_id   = db.Column(db.Integer)
    storey_name = db.Column(db.String)
    space_id    = db.Column(db.Integer)
    space_name  = db.Column(db.String)
    
    # Beziehung zu HVACComponent
    components  = db.relationship(
        "HVACComponent",
        back_populates="location",
        foreign_keys="[HVACComponent.location_id]"
    )

class HVACComponent(db.Model):
    __tablename__ = "hvac_components"

    # Primärschlüssel: KEIN foreign_key hier!
    id           = db.Column(db.Integer, primary_key=True)

    global_id    = db.Column(db.String,  unique=True, nullable=False)
    name         = db.Column(db.String)
    ifc_class    = db.Column(db.String,  nullable=False)
    object_type  = db.Column(db.String)
    properties   = db.Column(db.JSON)
    is_electronic = db.Column(db.Boolean, default=False)
    
    # BAS-Codes
    bas_code     = db.Column(db.String)
    bas_standard = db.Column(db.String)  # "amev" oder "vdi"

    # Fremdschlüssel
    model_id     = db.Column(db.Integer, db.ForeignKey("ifc_models.id"))
    system_id    = db.Column(db.Integer, db.ForeignKey("distribution_systems.id"))
    mapping_id   = db.Column(db.Integer, db.ForeignKey("classification_mappings.id"))
    location_id  = db.Column(db.Integer, db.ForeignKey("locations.id"))

    # Beziehungen
    model        = db.relationship(
        "IFCModel",
        back_populates="components",
        foreign_keys=[model_id]
    )
    system       = db.relationship(
        "DistributionSystem",
        back_populates="components",
        foreign_keys=[system_id]
    )
    mapping      = db.relationship(
        "ClassificationMapping",
        back_populates="components",
        foreign_keys=[mapping_id]
    )
    location     = db.relationship(
        "Location",
        back_populates="components",
        foreign_keys=[location_id]
    )
    
    @property
    def storey_name(self):
        """Liefert den Stockwerksnamen, wenn verfügbar"""
        return self.location.storey_name if self.location else None
    
    @property
    def space_name(self):
        """Liefert den Raumnamen, wenn verfügbar"""
        return self.location.space_name if self.location else None
    
    def to_dict(self):
        """Konvertiert das Objekt in ein Wörterbuch (für JSON-Serialisierung)"""
        result = {
            "element_id": self.id,
            "element_name": self.name,
            "element_type": self.ifc_class,
            "is_electronic": self.is_electronic,
            "bas_code": self.bas_code,
            "standard": self.bas_standard,
            "properties": self.properties
        }
        
        # Standortinformationen hinzufügen, falls vorhanden
        if self.location:
            result["location"] = {
                "storey_name": self.location.storey_name,
                "storey_id": self.location.storey_id,
                "space_name": self.location.space_name,
                "space_id": self.location.space_id
            }
        
        return result