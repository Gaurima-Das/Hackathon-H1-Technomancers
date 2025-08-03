from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from ..models import Resource, Project, ResourceAllocation, CapacityPlan, Report
from ..schemas import (
    ResourceCreate, ResourceUpdate, Resource as ResourceSchema,
    ProjectCreate, ProjectUpdate, Project as ProjectSchema,
    ResourceAllocationCreate, ResourceAllocationUpdate, ResourceAllocation as ResourceAllocationSchema,
    CapacityPlanCreate, CapacityPlanUpdate, CapacityPlan as CapacityPlanSchema,
    CapacityPlanningRequest, CapacityPlanningResponse,
    ReportGenerationRequest, Report as ReportSchema,
    ResourceList, ProjectList, AllocationList, PlanList, ReportList
)
from ..services.capacity_planning_service import CapacityPlanningService
from ..services.report_service import ReportService
from ..services.jira_service import JiraService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/capacity", tags=["capacity-planning"])

def get_capacity_service(db: Session = Depends(get_db)):
    jira_service = JiraService()
    return CapacityPlanningService(db, jira_service)

def get_report_service(db: Session = Depends(get_db)):
    return ReportService(db)

# Resource endpoints
@router.post("/resources", response_model=ResourceSchema)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    """Create a new resource"""
    db_resource = Resource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return ResourceSchema.from_orm(db_resource)

@router.get("/resources", response_model=ResourceList)
def get_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of resources"""
    resources = db.query(Resource).offset(skip).limit(limit).all()
    total = db.query(Resource).count()
    return ResourceList(
        resources=[ResourceSchema.from_orm(r) for r in resources],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/resources/{resource_id}", response_model=ResourceSchema)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """Get a specific resource"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceSchema.from_orm(resource)

@router.put("/resources/{resource_id}", response_model=ResourceSchema)
def update_resource(resource_id: int, resource_update: ResourceUpdate, db: Session = Depends(get_db)):
    """Update a resource"""
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    update_data = resource_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_resource, field, value)
    
    db.commit()
    db.refresh(db_resource)
    return ResourceSchema.from_orm(db_resource)

@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    """Delete a resource"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}

# Project endpoints
@router.post("/projects", response_model=ProjectSchema)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return ProjectSchema.from_orm(db_project)

@router.get("/projects", response_model=ProjectList)
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of projects"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    total = db.query(Project).count()
    return ProjectList(
        projects=[ProjectSchema.from_orm(p) for p in projects],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectSchema.from_orm(project)

@router.put("/projects/{project_id}", response_model=ProjectSchema)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return ProjectSchema.from_orm(db_project)

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

# Resource allocation endpoints
@router.post("/allocations", response_model=ResourceAllocationSchema)
def create_allocation(allocation: ResourceAllocationCreate, db: Session = Depends(get_db)):
    """Create a new resource allocation"""
    db_allocation = ResourceAllocation(**allocation.dict())
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return ResourceAllocationSchema.from_orm(db_allocation)

@router.get("/allocations", response_model=AllocationList)
def get_allocations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of resource allocations"""
    allocations = db.query(ResourceAllocation).offset(skip).limit(limit).all()
    total = db.query(ResourceAllocation).count()
    return AllocationList(
        allocations=[ResourceAllocationSchema.from_orm(a) for a in allocations],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/allocations/{allocation_id}", response_model=ResourceAllocationSchema)
def get_allocation(allocation_id: int, db: Session = Depends(get_db)):
    """Get a specific resource allocation"""
    allocation = db.query(ResourceAllocation).filter(ResourceAllocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Resource allocation not found")
    return ResourceAllocationSchema.from_orm(allocation)

@router.put("/allocations/{allocation_id}", response_model=ResourceAllocationSchema)
def update_allocation(allocation_id: int, allocation_update: ResourceAllocationUpdate, db: Session = Depends(get_db)):
    """Update a resource allocation"""
    db_allocation = db.query(ResourceAllocation).filter(ResourceAllocation.id == allocation_id).first()
    if not db_allocation:
        raise HTTPException(status_code=404, detail="Resource allocation not found")
    
    update_data = allocation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_allocation, field, value)
    
    db.commit()
    db.refresh(db_allocation)
    return ResourceAllocationSchema.from_orm(db_allocation)

@router.delete("/allocations/{allocation_id}")
def delete_allocation(allocation_id: int, db: Session = Depends(get_db)):
    """Delete a resource allocation"""
    allocation = db.query(ResourceAllocation).filter(ResourceAllocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="Resource allocation not found")
    
    db.delete(allocation)
    db.commit()
    return {"message": "Resource allocation deleted successfully"}

# Capacity planning endpoints
@router.post("/planning/generate", response_model=CapacityPlanningResponse)
def generate_capacity_plan(
    request: CapacityPlanningRequest,
    capacity_service: CapacityPlanningService = Depends(get_capacity_service)
):
    """Generate capacity planning with advanced algorithms"""
    try:
        return capacity_service.generate_capacity_plan(request)
    except Exception as e:
        logger.error(f"Error generating capacity plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {str(e)}")

@router.get("/plans", response_model=PlanList)
def get_capacity_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of capacity plans"""
    plans = db.query(CapacityPlan).offset(skip).limit(limit).all()
    total = db.query(CapacityPlan).count()
    return PlanList(
        plans=[CapacityPlanSchema.from_orm(p) for p in plans],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/plans/{plan_id}", response_model=CapacityPlanSchema)
def get_capacity_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a specific capacity plan"""
    plan = db.query(CapacityPlan).filter(CapacityPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Capacity plan not found")
    return CapacityPlanSchema.from_orm(plan)

@router.put("/plans/{plan_id}", response_model=CapacityPlanSchema)
def update_capacity_plan(plan_id: int, plan_update: CapacityPlanUpdate, db: Session = Depends(get_db)):
    """Update a capacity plan"""
    db_plan = db.query(CapacityPlan).filter(CapacityPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Capacity plan not found")
    
    update_data = plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_plan, field, value)
    
    db.commit()
    db.refresh(db_plan)
    return CapacityPlanSchema.from_orm(db_plan)

@router.delete("/plans/{plan_id}")
def delete_capacity_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a capacity plan"""
    plan = db.query(CapacityPlan).filter(CapacityPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Capacity plan not found")
    
    db.delete(plan)
    db.commit()
    return {"message": "Capacity plan deleted successfully"}

# Report endpoints
@router.post("/reports/generate", response_model=ReportSchema)
def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    report_service: ReportService = Depends(get_report_service)
):
    """Generate capacity planning report"""
    try:
        return report_service.generate_monthly_report(request)
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/reports", response_model=ReportList)
def get_reports(skip: int = 0, limit: int = 100, report_service: ReportService = Depends(get_report_service)):
    """Get list of reports"""
    reports = report_service.get_reports(skip, limit)
    total = len(reports)  # This should be improved with proper counting
    return ReportList(
        reports=reports,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/reports/{report_id}", response_model=ReportSchema)
def get_report(report_id: int, report_service: ReportService = Depends(get_report_service)):
    """Get a specific report"""
    report = report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# Forecast endpoint
@router.get("/forecast")
def get_capacity_forecast(
    months_ahead: int = 12,
    capacity_service: CapacityPlanningService = Depends(get_capacity_service)
):
    """Get capacity forecast for future months"""
    try:
        return capacity_service.get_capacity_forecast(months_ahead)
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}") 