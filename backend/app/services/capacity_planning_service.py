from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

from ..models import Resource, Project, ResourceAllocation, CapacityPlan
from ..schemas import CapacityPlanningRequest, CapacityPlanningResponse
from .jira_service import JiraService

logger = logging.getLogger(__name__)

class CapacityPlanningService:
    def __init__(self, db: Session, jira_service: JiraService):
        self.db = db
        self.jira_service = jira_service
    
    def generate_capacity_plan(self, request: CapacityPlanningRequest) -> CapacityPlanningResponse:
        """Generate comprehensive capacity planning with advanced algorithms"""
        try:
            # Sync projects from Jira if needed
            self._sync_projects_from_jira()
            
            # Get resources and projects for the planning period
            resources = self._get_resources(request.resource_types)
            projects = self._get_projects_in_period(request.start_date, request.end_date)
            
            # Generate capacity plans using multiple algorithms
            plans = []
            summary = {}
            recommendations = []
            
            # Algorithm 1: Load Balancing
            load_balanced_plans = self._load_balancing_algorithm(resources, projects, request)
            plans.extend(load_balanced_plans)
            
            # Algorithm 2: Cost Optimization
            cost_optimized_plans = self._cost_optimization_algorithm(resources, projects, request)
            plans.extend(cost_optimized_plans)
            
            # Algorithm 3: Efficiency Maximization
            efficiency_plans = self._efficiency_maximization_algorithm(resources, projects, request)
            plans.extend(efficiency_plans)
            
            # Generate summary statistics
            summary = self._generate_summary_statistics(plans, resources, projects)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(plans, summary, request)
            
            return CapacityPlanningResponse(
                plans=plans,
                summary=summary,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating capacity plan: {e}")
            raise
    
    def _sync_projects_from_jira(self):
        """Sync projects from Jira to local database"""
        try:
            # Get projects from Jira
            jira_projects = self.jira_service.get_projects()
            
            for jira_project in jira_projects:
                # Check if project already exists
                existing_project = self.db.query(Project).filter(
                    Project.name == jira_project['name']
                ).first()
                
                if not existing_project:
                    # Create new project from Jira data
                    project = Project(
                        name=jira_project['name'],
                        description=jira_project.get('description', ''),
                        start_date=datetime.now(),  # Default start date
                        end_date=datetime.now() + timedelta(days=365),  # Default end date
                        status='active',
                        priority='medium',
                        requirements={'capacity': jira_project.get('storyPoints', 0) * 8}  # Convert story points to hours
                    )
                    self.db.add(project)
            
            self.db.commit()
            logger.info(f"Synced {len(jira_projects)} projects from Jira")
            
        except Exception as e:
            logger.error(f"Error syncing projects from Jira: {e}")
            self.db.rollback()
    
    def _get_resources(self, resource_types: Optional[List[str]] = None) -> List[Resource]:
        """Get available resources filtered by type"""
        query = self.db.query(Resource).filter(Resource.is_active == True)
        
        if resource_types:
            query = query.filter(Resource.type.in_(resource_types))
        
        resources = query.all()
        
        # If no resources exist, create some default ones
        if not resources:
            resources = self._create_default_resources()
        
        return resources
    
    def _create_default_resources(self) -> List[Resource]:
        """Create default resources based on Jira users"""
        try:
            # Get users from Jira
            jira_users = self.jira_service.get_users()
            resources = []
            
            for user in jira_users[:10]:  # Limit to first 10 users
                resource = Resource(
                    name=user.get('displayName', user.get('name', 'Unknown')),
                    type='human',
                    capacity=40.0,  # 40 hours per week
                    available_capacity=40.0,
                    cost_per_unit=100.0,  # $100 per hour
                    location='Remote',
                    skills={'jira_user': True, 'active': user.get('active', True)}
                )
                self.db.add(resource)
                resources.append(resource)
            
            self.db.commit()
            logger.info(f"Created {len(resources)} default resources from Jira users")
            return resources
            
        except Exception as e:
            logger.error(f"Error creating default resources: {e}")
            self.db.rollback()
            return []
    
    def _get_projects_in_period(self, start_date: datetime, end_date: datetime) -> List[Project]:
        """Get projects that overlap with the planning period"""
        return self.db.query(Project).filter(
            and_(
                Project.start_date <= end_date,
                Project.end_date >= start_date,
                Project.status.in_(["planned", "active"])
            )
        ).all()
    
    def _load_balancing_algorithm(self, resources: List[Resource], projects: List[Project], request: CapacityPlanningRequest) -> List[CapacityPlan]:
        """Load balancing algorithm to distribute workload evenly"""
        plans = []
        
        # Calculate total required capacity
        total_required = sum(project.requirements.get('capacity', 0) for project in projects)
        total_available = sum(resource.available_capacity for resource in resources)
        
        if total_required > total_available:
            # Over-capacity scenario - prioritize based on project priority
            projects.sort(key=lambda p: self._get_priority_score(p.priority), reverse=True)
        
        # Distribute workload using weighted round-robin
        resource_index = 0
        for project in projects:
            required_capacity = project.requirements.get('capacity', 0)
            
            while required_capacity > 0 and resource_index < len(resources):
                resource = resources[resource_index]
                
                # Calculate allocation for this resource
                allocation = min(required_capacity, resource.available_capacity)
                
                if allocation > 0:
                    # Create capacity plan
                    plan = CapacityPlan(
                        resource_id=resource.id,
                        project_id=project.id,
                        month=request.start_date.month,
                        year=request.start_date.year,
                        planned_capacity=allocation,
                        utilization_rate=allocation / resource.capacity,
                        efficiency_score=self._calculate_efficiency_score(resource, project, allocation)
                    )
                    plans.append(plan)
                    
                    required_capacity -= allocation
                    resource.available_capacity -= allocation
                
                resource_index = (resource_index + 1) % len(resources)
        
        return plans
    
    def _cost_optimization_algorithm(self, resources: List[Resource], projects: List[Project], request: CapacityPlanningRequest) -> List[CapacityPlan]:
        """Cost optimization algorithm to minimize total cost"""
        plans = []
        
        # Sort resources by cost per unit (ascending)
        resources_sorted = sorted(resources, key=lambda r: r.cost_per_unit)
        
        for project in projects:
            required_capacity = project.requirements.get('capacity', 0)
            remaining_requirement = required_capacity
            
            # Allocate to cheapest resources first
            for resource in resources_sorted:
                if remaining_requirement <= 0:
                    break
                
                if resource.available_capacity > 0:
                    allocation = min(remaining_requirement, resource.available_capacity)
                    
                    plan = CapacityPlan(
                        resource_id=resource.id,
                        project_id=project.id,
                        month=request.start_date.month,
                        year=request.start_date.year,
                        planned_capacity=allocation,
                        utilization_rate=allocation / resource.capacity,
                        efficiency_score=self._calculate_efficiency_score(resource, project, allocation)
                    )
                    plans.append(plan)
                    
                    remaining_requirement -= allocation
                    resource.available_capacity -= allocation
        
        return plans
    
    def _efficiency_maximization_algorithm(self, resources: List[Resource], projects: List[Project], request: CapacityPlanningRequest) -> List[CapacityPlan]:
        """Efficiency maximization algorithm to optimize resource efficiency"""
        plans = []
        
        for project in projects:
            required_capacity = project.requirements.get('capacity', 0)
            remaining_requirement = required_capacity
            
            # Find resources with best efficiency scores for this project
            resource_efficiency = []
            for resource in resources:
                if resource.available_capacity > 0:
                    efficiency = self._calculate_efficiency_score(resource, project, min(required_capacity, resource.available_capacity))
                    resource_efficiency.append((resource, efficiency))
            
            # Sort by efficiency score (descending)
            resource_efficiency.sort(key=lambda x: x[1], reverse=True)
            
            # Allocate to most efficient resources first
            for resource, efficiency in resource_efficiency:
                if remaining_requirement <= 0:
                    break
                
                allocation = min(remaining_requirement, resource.available_capacity)
                
                plan = CapacityPlan(
                    resource_id=resource.id,
                    project_id=project.id,
                    month=request.start_date.month,
                    year=request.start_date.year,
                    planned_capacity=allocation,
                    utilization_rate=allocation / resource.capacity,
                    efficiency_score=efficiency
                )
                plans.append(plan)
                
                remaining_requirement -= allocation
                resource.available_capacity -= allocation
        
        return plans
    
    def _calculate_efficiency_score(self, resource: Resource, project: Project, allocation: float) -> float:
        """Calculate efficiency score for resource-project allocation"""
        base_score = 0.5
        
        # Resource type matching
        if resource.type == 'human' and 'human' in str(project.requirements):
            base_score += 0.2
        
        # Skills matching
        if resource.skills and 'jira_user' in resource.skills:
            base_score += 0.1
        
        # Capacity utilization
        utilization = allocation / resource.capacity
        if utilization > 0.8:
            base_score += 0.1  # Bonus for high utilization
        
        return min(base_score, 1.0)
    
    def _get_priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score"""
        priority_scores = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        return priority_scores.get(priority, 2)
    
    def _generate_summary_statistics(self, plans: List[CapacityPlan], resources: List[Resource], projects: List[Project]) -> Dict[str, Any]:
        """Generate summary statistics for the capacity plan"""
        if not plans:
            return {}
        
        total_planned_capacity = sum(plan.planned_capacity for plan in plans)
        total_available_capacity = sum(resource.capacity for resource in resources)
        total_required_capacity = sum(project.requirements.get('capacity', 0) for project in projects)
        
        avg_utilization = sum(plan.utilization_rate for plan in plans) / len(plans)
        avg_efficiency = sum(plan.efficiency_score for plan in plans) / len(plans)
        
        # Calculate cost metrics
        total_cost = sum(plan.planned_capacity * plan.resource.cost_per_unit for plan in plans)
        
        return {
            "total_planned_capacity": total_planned_capacity,
            "total_available_capacity": total_available_capacity,
            "total_required_capacity": total_required_capacity,
            "capacity_utilization_rate": total_planned_capacity / total_available_capacity if total_available_capacity > 0 else 0,
            "requirement_satisfaction_rate": total_planned_capacity / total_required_capacity if total_required_capacity > 0 else 0,
            "average_utilization_rate": avg_utilization,
            "average_efficiency_score": avg_efficiency,
            "total_cost": total_cost,
            "number_of_plans": len(plans),
            "number_of_resources": len(resources),
            "number_of_projects": len(projects)
        }
    
    def _generate_recommendations(self, plans: List[CapacityPlan], summary: Dict[str, Any], request: CapacityPlanningRequest) -> List[str]:
        """Generate recommendations based on capacity plan analysis"""
        recommendations = []
        
        # Capacity utilization recommendations
        if summary.get("capacity_utilization_rate", 0) < 0.7:
            recommendations.append("Consider increasing resource utilization to improve efficiency")
        elif summary.get("capacity_utilization_rate", 0) > 0.95:
            recommendations.append("High utilization detected - consider adding more resources to prevent bottlenecks")
        
        # Requirement satisfaction recommendations
        if summary.get("requirement_satisfaction_rate", 0) < 0.9:
            recommendations.append("Not all project requirements can be satisfied with current resources")
        
        # Efficiency recommendations
        if summary.get("average_efficiency_score", 0) < 0.6:
            recommendations.append("Low efficiency scores detected - review resource-project assignments")
        
        # Cost recommendations
        if summary.get("total_cost", 0) > 1000000:  # Example threshold
            recommendations.append("High total cost - consider cost optimization strategies")
        
        # Resource recommendations
        if summary.get("number_of_resources", 0) < summary.get("number_of_projects", 0):
            recommendations.append("More projects than resources - consider resource sharing or additional resources")
        
        return recommendations
    
    def get_capacity_forecast(self, months_ahead: int = 12) -> Dict[str, Any]:
        """Generate capacity forecast for future months"""
        forecast = {}
        
        for i in range(months_ahead):
            date = datetime.now() + timedelta(days=30*i)
            month = date.month
            year = date.year
            
            # Get historical data for trend analysis
            historical_plans = self.db.query(CapacityPlan).filter(
                and_(
                    CapacityPlan.month == month,
                    CapacityPlan.year < year
                )
            ).all()
            
            if historical_plans:
                avg_utilization = sum(plan.utilization_rate for plan in historical_plans) / len(historical_plans)
                forecast[f"{year}-{month:02d}"] = {
                    "predicted_utilization": avg_utilization,
                    "confidence_level": 0.8 if len(historical_plans) > 5 else 0.6
                }
        
        return forecast 