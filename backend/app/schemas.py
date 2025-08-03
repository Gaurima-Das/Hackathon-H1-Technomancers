from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Enums
class ResourceType(str, Enum):
    HUMAN = "human"
    EQUIPMENT = "equipment"
    FACILITY = "facility"

class ProjectStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReportType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"

class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"

# Base Models
class ResourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: ResourceType
    capacity: float = Field(..., gt=0)
    available_capacity: float = Field(..., ge=0)
    cost_per_unit: float = Field(..., ge=0)
    location: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    specifications: Optional[Dict[str, Any]] = None
    is_active: bool = True

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: ProjectStatus = ProjectStatus.PLANNED
    priority: ProjectPriority = ProjectPriority.MEDIUM
    budget: Optional[float] = None
    manager: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None

class ResourceAllocationBase(BaseModel):
    resource_id: int
    project_id: int
    start_date: datetime
    end_date: datetime
    allocated_capacity: float = Field(..., gt=0)
    actual_usage: float = Field(default=0.0, ge=0)
    status: str = "allocated"
    notes: Optional[str] = None

class CapacityPlanBase(BaseModel):
    resource_id: int
    project_id: int
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)
    planned_capacity: float = Field(..., ge=0)
    actual_capacity: float = Field(default=0.0, ge=0)
    utilization_rate: float = Field(default=0.0, ge=0, le=1)
    efficiency_score: float = Field(default=0.0, ge=0, le=1)

class ReportBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    type: ReportType
    period_start: datetime
    period_end: datetime
    format: ReportFormat = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = None
    generated_by: Optional[str] = None

# Create Models
class ResourceCreate(ResourceBase):
    pass

class ProjectCreate(ProjectBase):
    pass

class ResourceAllocationCreate(ResourceAllocationBase):
    pass

class CapacityPlanCreate(CapacityPlanBase):
    pass

class ReportCreate(ReportBase):
    pass

# Update Models
class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[ResourceType] = None
    capacity: Optional[float] = Field(None, gt=0)
    available_capacity: Optional[float] = Field(None, ge=0)
    cost_per_unit: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    specifications: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    budget: Optional[float] = None
    manager: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None

class ResourceAllocationUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    allocated_capacity: Optional[float] = Field(None, gt=0)
    actual_usage: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None
    notes: Optional[str] = None

class CapacityPlanUpdate(BaseModel):
    planned_capacity: Optional[float] = Field(None, ge=0)
    actual_capacity: Optional[float] = Field(None, ge=0)
    utilization_rate: Optional[float] = Field(None, ge=0, le=1)
    efficiency_score: Optional[float] = Field(None, ge=0, le=1)

# Response Models
class Resource(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResourceAllocation(ResourceAllocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    resource: Optional[Resource] = None
    project: Optional[Project] = None

    class Config:
        from_attributes = True

class CapacityPlan(CapacityPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    resource: Optional[Resource] = None
    project: Optional[Project] = None

    class Config:
        from_attributes = True

class Report(ReportBase):
    id: int
    status: str
    file_path: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Specialized schemas
class CapacityPlanningRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    resource_types: Optional[List[ResourceType]] = None
    include_historical: bool = True
    optimization_target: str = "utilization"  # utilization, cost, efficiency

class CapacityPlanningResponse(BaseModel):
    plans: List[CapacityPlan]
    summary: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime

class ReportGenerationRequest(BaseModel):
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    format: ReportFormat = ReportFormat.PDF
    include_charts: bool = True
    include_details: bool = True
    recipients: Optional[List[str]] = None

class ExportRequest(BaseModel):
    data_type: str  # resources, projects, allocations, plans, reports
    format: str = "excel"  # excel, csv, json
    filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = True

# List response schemas
class ResourceList(BaseModel):
    resources: List[Resource]
    total: int
    page: int
    size: int

class ProjectList(BaseModel):
    projects: List[Project]
    total: int
    page: int
    size: int

class AllocationList(BaseModel):
    allocations: List[ResourceAllocation]
    total: int
    page: int
    size: int

class PlanList(BaseModel):
    plans: List[CapacityPlan]
    total: int
    page: int
    size: int

class ReportList(BaseModel):
    reports: List[Report]
    total: int
    page: int
    size: int 