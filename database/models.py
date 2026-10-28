from datetime import datetime, timezone
from database.database import db

class ProcessState:
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    DEADLOCKED = "DEADLOCKED"
    TERMINATED = "TERMINATED"

class Process(db.Model):
    __tablename__ = 'processes'

    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(20), default=ProcessState.READY, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    allocations = db.relationship('Allocation', backref='process', cascade='all, delete-orphan', lazy='joined')
    maximums = db.relationship('MaximumNeed', backref='process', cascade='all, delete-orphan', lazy='joined')
    requests = db.relationship('ResourceRequest', backref='process', cascade='all, delete-orphan', lazy='select')

    def to_dict(self):
        alloc_dict = {a.resource.resource_id: a.allocated for a in self.allocations if a.resource}
        max_dict = {m.resource.resource_id: m.maximum for m in self.maximums if m.resource}
        need_dict = {}
        for r_id in max_dict:
            need_dict[r_id] = max(0, max_dict.get(r_id, 0) - alloc_dict.get(r_id, 0))

        # Check pending requests
        pending_req = next((r.request_data for r in self.requests if r.status == 'PENDING'), None)

        return {
            'id': self.id,
            'pid': self.pid,
            'name': self.name,
            'state': self.state,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'allocation': alloc_dict,
            'maximum': max_dict,
            'need': need_dict,
            'pending_request': pending_req
        }

class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    total_instances = db.Column(db.Integer, nullable=False, default=1)
    available_instances = db.Column(db.Integer, nullable=False, default=1)

    allocations = db.relationship('Allocation', backref='resource', cascade='all, delete-orphan', lazy='joined')
    maximums = db.relationship('MaximumNeed', backref='resource', cascade='all, delete-orphan', lazy='select')

    def to_dict(self):
        allocated_count = sum(a.allocated for a in self.allocations)
        utilization = round((allocated_count / self.total_instances * 100), 1) if self.total_instances > 0 else 0.0
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'name': self.name,
            'total_instances': self.total_instances,
            'available_instances': self.available_instances,
            'allocated_instances': allocated_count,
            'utilization_percent': utilization
        }

class Allocation(db.Model):
    __tablename__ = 'allocations'

    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', ondelete='CASCADE'), nullable=False)
    allocated = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('process_id', 'resource_id', name='uq_process_resource_alloc'),
    )

class MaximumNeed(db.Model):
    __tablename__ = 'maximum_needs'

    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', ondelete='CASCADE'), nullable=False)
    maximum = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('process_id', 'resource_id', name='uq_process_resource_max'),
    )

class ResourceRequest(db.Model):
    __tablename__ = 'resource_requests'

    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id', ondelete='CASCADE'), nullable=False)
    request_data = db.Column(db.JSON, nullable=False)  # Dict e.g. {"R0": 1, "R1": 0}
    status = db.Column(db.String(20), default='PENDING', nullable=False)  # PENDING, GRANTED, DENIED, CANCELLED
    reason = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'process_id': self.process_id,
            'pid': self.process.pid if self.process else None,
            'process_name': self.process.name if self.process else None,
            'request_data': self.request_data,
            'status': self.status,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class EventLog(db.Model):
    __tablename__ = 'event_logs'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }

class Scenario(db.Model):
    __tablename__ = 'scenarios'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    configuration = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'configuration': self.configuration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
