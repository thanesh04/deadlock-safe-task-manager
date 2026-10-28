"""
Resource Manager: CRUD and synchronization of system resources and instances.
"""
from typing import Dict, List, Tuple, Any, Optional
from database.database import db
from database.models import Resource, Allocation, MaximumNeed, Process, EventLog
from simulation.validation import SimulationValidator

class ResourceManager:
    @staticmethod
    def get_all_resources() -> List[Resource]:
        return Resource.query.order_by(Resource.resource_id).all()

    @staticmethod
    def get_by_id(res_id: int) -> Optional[Resource]:
        return db.session.get(Resource, res_id)

    @staticmethod
    def get_by_resource_id(rid: str) -> Optional[Resource]:
        return Resource.query.filter_by(resource_id=rid.upper()).first()

    @staticmethod
    def create_resource(resource_id: str, name: str, total_instances: int) -> Tuple[bool, str, Optional[Resource]]:
        resource_id = resource_id.strip().upper()
        existing = [r.resource_id for r in Resource.query.all()]
        valid, msg = SimulationValidator.validate_resource_data(resource_id, name, total_instances, existing)
        if not valid:
            return False, msg, None

        resource = Resource(
            resource_id=resource_id,
            name=name.strip(),
            total_instances=total_instances,
            available_instances=total_instances
        )
        db.session.add(resource)
        db.session.flush()

        # Create zero allocation and maximum for all existing processes
        processes = Process.query.all()
        for p in processes:
            db.session.add(Allocation(process_id=p.id, resource_id=resource.id, allocated=0))
            db.session.add(MaximumNeed(process_id=p.id, resource_id=resource.id, maximum=0))

        log = EventLog(
            event_type="RESOURCE_CREATED",
            description=f"Created resource '{name}' ({resource_id}) with {total_instances} instances."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Resource {resource_id} created successfully.", resource

    @staticmethod
    def update_resource(res_id: int, name: str, total_instances: int) -> Tuple[bool, str]:
        resource = db.session.get(Resource, res_id)
        if not resource:
            return False, "Resource not found."

        if total_instances < 1:
            return False, "Total instances must be at least 1."

        allocated_count = sum(a.allocated for a in resource.allocations)
        if total_instances < allocated_count:
            return False, f"Cannot reduce total instances to {total_instances}; {allocated_count} instances are currently allocated."

        resource.name = name.strip()
        resource.total_instances = total_instances
        resource.available_instances = total_instances - allocated_count

        log = EventLog(
            event_type="RESOURCE_UPDATED",
            description=f"Updated resource {resource.resource_id}: total={total_instances}, available={resource.available_instances}."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Resource {resource.resource_id} updated successfully."

    @staticmethod
    def delete_resource(res_id: int) -> Tuple[bool, str]:
        resource = db.session.get(Resource, res_id)
        if not resource:
            return False, "Resource not found."

        allocated_count = sum(a.allocated for a in resource.allocations)
        if allocated_count > 0:
            return False, f"Cannot delete resource {resource.resource_id} while it has active allocations ({allocated_count} allocated)."

        rid = resource.resource_id
        db.session.delete(resource)
        log = EventLog(
            event_type="RESOURCE_DELETED",
            description=f"Deleted resource {rid}."
        )
        db.session.add(log)
        db.session.commit()
        return True, f"Resource {rid} deleted."

    @staticmethod
    def recalculate_available(resource_id: Optional[int] = None):
        """Ensures available_instances = total_instances - sum(allocated) across resources."""
        query = Resource.query
        if resource_id:
            query = query.filter_by(id=resource_id)
        resources = query.all()
        for r in resources:
            allocated = sum(a.allocated for a in r.allocations)
            r.available_instances = max(0, r.total_instances - allocated)
        db.session.commit()
