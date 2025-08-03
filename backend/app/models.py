from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Sprint(Base):
    __tablename__ = "sprints"
    
    id = Column(Integer, primary_key=True, index=True)
    jira_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    state = Column(String)  # active, closed, future
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    goal = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    issues = relationship("Issue", back_populates="sprint")

class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    jira_key = Column(String, unique=True, index=True)
    summary = Column(String)
    description = Column(Text)
    issue_type = Column(String)  # Story, Bug, Task, etc.
    status = Column(String)
    priority = Column(String)
    assignee = Column(String)
    reporter = Column(String)
    story_points = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    due_date = Column(DateTime)
    sprint_id = Column(Integer, ForeignKey("sprints.id"))
    
    sprint = relationship("Sprint", back_populates="issues")
    work_logs = relationship("WorkLog", back_populates="issue")

class WorkLog(Base):
    __tablename__ = "work_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    jira_id = Column(Integer, unique=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    author = Column(String)
    comment = Column(Text)
    time_spent_seconds = Column(Integer)
    started_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    issue = relationship("Issue", back_populates="work_logs")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    jira_username = Column(String, unique=True, index=True)
    display_name = Column(String)
    email = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_type = Column(String)  # missing_worklog, due_date, missing_epic
    message = Column(Text)
    issue_key = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Capacity Planning Models
class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # human, equipment, facility
    capacity = Column(Float)
    available_capacity = Column(Float)
    cost_per_unit = Column(Float)
    location = Column(String)
    skills = Column(JSON)  # Store skills as JSON
    specifications = Column(JSON)  # Store specifications as JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    allocations = relationship("ResourceAllocation", back_populates="resource")
    capacity_plans = relationship("CapacityPlan", back_populates="resource")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)  # planned, active, completed, cancelled
    priority = Column(String)  # low, medium, high, critical
    budget = Column(Float)
    manager = Column(String)
    requirements = Column(JSON)  # Store requirements as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    allocations = relationship("ResourceAllocation", back_populates="project")
    capacity_plans = relationship("CapacityPlan", back_populates="project")

class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    allocated_capacity = Column(Float)
    actual_usage = Column(Float, default=0.0)
    status = Column(String, default="allocated")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resource = relationship("Resource", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")

class CapacityPlan(Base):
    __tablename__ = "capacity_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    month = Column(Integer)
    year = Column(Integer)
    planned_capacity = Column(Float)
    actual_capacity = Column(Float, default=0.0)
    utilization_rate = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resource = relationship("Resource", back_populates="capacity_plans")
    project = relationship("Project", back_populates="capacity_plans")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String)  # monthly, quarterly, annual, custom
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    format = Column(String)  # pdf, excel, html
    parameters = Column(JSON)  # Store parameters as JSON
    status = Column(String, default="pending")  # pending, generating, completed, failed
    file_path = Column(String)
    generated_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime) 