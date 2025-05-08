import ifcopenshell
import ifcopenshell.util.system
from models import db, IFCModel, HVACComponent, DistributionSystem

def extract_and_persist(ifc_path, model_record):
    model = ifcopenshell.open(ifc_path)
    hvac_types = [
        "IfcFlowTerminal", "IfcPipeSegment", "IfcDuctSegment",
        "IfcFlowFitting", "IfcPipeFitting", "IfcDuctFitting",
        "IfcFlowController", "IfcValve", "IfcDamper",
        "IfcFlowMovingDevice", "IfcPump", "IfcFan",
        "IfcEnergyConversionDevice", "IfcBoiler", "IfcChiller",
        "IfcFlowStorageDevice", "IfcTank",
        "IfcFlowTreatmentDevice", "IfcFilter"
    ]
    for cls in hvac_types:
        for elem in model.by_type(cls):
            name = elem.Name or None
            gid = elem.GlobalId
            systems = ifcopenshell.util.system.get_element_systems(elem)
            if systems:
                sys = systems[0]
                system_record = DistributionSystem.query.filter_by(name=sys.Name).first()
                if not system_record:
                    system_record = DistributionSystem(
                        name=sys.Name,
                        predefined_type=getattr(sys, "PredefinedType", None)
                    )
                    db.session.add(system_record)
                    db.session.commit()
            else:
                system_record = None
            comp = HVACComponent(
                global_id=gid,
                name=name,
                ifc_class=elem.is_a(),
                object_type=getattr(elem, "PredefinedType", None),
                properties={},
                model=model_record,
                system=system_record
            )
            db.session.add(comp)
    db.session.commit()
