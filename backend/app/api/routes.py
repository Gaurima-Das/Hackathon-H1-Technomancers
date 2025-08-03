from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_db
from ..services.jira_service import JiraService
from ..services.ai_service import AIService
try:
    from ..services.outlook_service import OutlookService
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False
    print("Warning: O365 module not available. Outlook integration disabled.")
from ..config import settings

router = APIRouter()

# Initialize services
jira_service = JiraService()
ai_service = None  # Will be initialized when API key is provided
outlook_service = None  # Will be initialized when credentials are provided

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@router.post("/connect")
async def connect_jira(server: str, email: str, api_token: str):
    """Connect to Jira with credentials"""
    global jira_service
    jira_service = JiraService(server, email, api_token)
    
    if jira_service.connect():
        return {"status": "connected", "message": "Successfully connected to Jira"}
    else:
        raise HTTPException(status_code=400, detail="Failed to connect to Jira")

@router.get("/sprints")
async def get_sprints():
    """Get all active sprints"""
    try:
        sprints = jira_service.get_active_sprints()
        return {"sprints": sprints}
    except Exception as e:
        print(f"Error in get_sprints endpoint: {e}")
        return {"sprints": [], "error": str(e)}

@router.get("/sprint/{sprint_id}")
async def get_sprint_details(sprint_id: int):
    """Get detailed information about a specific sprint"""
    issues = jira_service.get_sprint_issues(sprint_id)
    burndown = jira_service.get_sprint_burndown(sprint_id)
    
    return {
        "sprint_id": sprint_id,
        "issues": issues,
        "burndown": burndown,
        "total_issues": len(issues)
    }

@router.get("/sprint/{sprint_id}/report")
async def get_sprint_report(sprint_id: int):
    """Get comprehensive sprint report"""
    issues = jira_service.get_sprint_issues(sprint_id)
    burndown = jira_service.get_sprint_burndown(sprint_id)
    
    # Calculate additional metrics
    status_counts = {}
    assignee_counts = {}
    total_points = 0
    completed_points = 0
    
    for issue in issues:
        status = issue.get('status', 'Unknown')
        assignee = issue.get('assignee', 'Unassigned')
        points = issue.get('story_points', 0) or 0
        
        status_counts[status] = status_counts.get(status, 0) + 1
        assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        total_points += points
        
        if status == 'CLOSED':
            completed_points += points
    
    return {
        "sprint_id": sprint_id,
        "summary": {
            "total_issues": len(issues),
            "total_points": total_points,
            "completed_points": completed_points,
            "completion_percentage": (completed_points / total_points * 100) if total_points > 0 else 0
        },
        "status_distribution": status_counts,
        "assignee_distribution": assignee_counts,
        "burndown": burndown,
        "issues": issues
    }

@router.get("/user/{username}/worklogs")
async def get_user_worklogs(username: str, period: str = Query("7d", description="Time period: 7d, 30d, 3m, 6m, 1y, all")):
    """Get work logs for a specific user"""
    try:
        # First check if user exists
        user_exists = jira_service.check_user_exists(username)
        if not user_exists:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in Jira")
        
        worklogs = jira_service.get_user_worklogs(username, period)
        
        # Calculate summary statistics
        total_time = sum(wl.get('time_spent_seconds', 0) for wl in worklogs)
        total_hours = total_time / 3600
        
        return {
            "username": username,
            "period": period,
            "total_worklogs": len(worklogs),
            "total_hours": round(total_hours, 2),
            "worklogs": worklogs
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching work logs: {str(e)}")



@router.get("/user/{username}/issues")
async def get_user_issues(username: str):
    """Get all issues assigned to a user"""
    try:
        # First check if user exists
        user_exists = jira_service.check_user_exists(username)
        if not user_exists:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in Jira")
        
        issues = jira_service.get_user_issues(username)
        
        # Calculate summary
        total_points = sum(issue.get('story_points', 0) or 0 for issue in issues)
        priority_counts = {}
        
        for issue in issues:
            priority = issue.get('priority', 'None')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "username": username,
            "total_issues": len(issues),
            "total_points": total_points,
            "priority_distribution": priority_counts,
            "issues": issues
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user issues: {str(e)}")

@router.get("/capacity")
async def get_team_capacity(
    team_members: str = Query(..., description="Comma-separated list of usernames"),
    sprint_id: int = Query(None, description="Optional single sprint ID to filter by"),
    sprint_ids: str = Query(None, description="Optional comma-separated list of sprint IDs")
):
    """Get capacity information for team members"""
    members = [member.strip() for member in team_members.split(',')]
    
    # Handle multiple sprint IDs
    if sprint_ids:
        sprint_id_list = [int(sid.strip()) for sid in sprint_ids.split(',')]
        capacity_data = jira_service.get_team_capacity_multiple_sprints(members, sprint_id_list)
    else:
        capacity_data = jira_service.get_team_capacity(members, sprint_id)
    
    # Calculate team totals
    team_total_issues = sum(data.get('total_issues', 0) for data in capacity_data.values())
    team_total_points = sum(data.get('total_points', 0) for data in capacity_data.values())
    
    return {
        "team_members": members,
        "sprint_id": sprint_id,
        "sprint_ids": sprint_ids,
        "team_summary": {
            "total_issues": team_total_issues,
            "total_points": team_total_points
        },
        "member_details": capacity_data
    }

@router.get("/alerts")
async def get_alerts(username: str = Query(..., description="Username to check alerts for")):
    """Get alerts for a user"""
    try:
        # First check if user exists
        user_exists = jira_service.check_user_exists(username)
        if not user_exists:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in Jira")
        
        # Check for missing work logs
        worklogs = jira_service.get_user_worklogs(username, period="1d")
        issues = jira_service.get_user_issues(username)
        
        alerts = []
        
        # Check for missing work logs from yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        has_yesterday_worklog = any(
            wl.get('started', '').startswith(yesterday) 
            for wl in worklogs
        )
        
        if not has_yesterday_worklog:
            alerts.append({
                "type": "missing_worklog",
                "message": f"No work log found for {yesterday}",
                "severity": "medium"
            })
        
        # Check for due dates
        today = datetime.now().date()
        for issue in issues:
            due_date = issue.get('due_date')
            if due_date:
                try:
                    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                    if due_date_obj < today:
                        alerts.append({
                            "type": "overdue",
                            "message": f"Issue {issue['key']} is overdue",
                            "issue_key": issue['key'],
                            "severity": "high"
                        })
                    elif due_date_obj == today:
                        alerts.append({
                            "type": "due_today",
                            "message": f"Issue {issue['key']} is due today",
                            "issue_key": issue['key'],
                            "severity": "medium"
                        })
                except:
                    pass
        
        return {
            "username": username,
            "alerts": alerts,
            "total_alerts": len(alerts)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.get("/reports/monthly")
async def generate_monthly_report(month: int = Query(..., ge=1, le=12), year: int = Query(..., ge=2020)):
    """Generate monthly report"""
    try:
        # Get monthly report data from Jira service
        report_data = jira_service.get_monthly_report(month, year)
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating monthly report: {str(e)}")

@router.post("/organize-tasks")
async def organize_tasks(
    username: str = Query(..., description="Username to organize tasks for"),
    openai_api_key: str = Query(..., description="OpenAI API key for task organization"),
    work_hours_per_day: int = Query(8, description="Working hours per day", ge=1, le=24),
    work_days: str = Query("Monday,Tuesday,Wednesday,Thursday,Friday", description="Comma-separated list of work days")
):
    """Organize user tasks using AI based on priority and time allocation"""
    try:
        # Initialize AI service
        global ai_service
        ai_service = AIService(openai_api_key)
        
        # First check if user exists
        user_exists = jira_service.check_user_exists(username)
        if not user_exists:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in Jira")
        
        # Get user issues
        issues = jira_service.get_user_issues(username)
        
        if not issues:
            return {
                "message": "No tasks found to organize",
                "summary": {
                    "total_tasks": 0,
                    "total_hours": 0,
                    "available_hours": work_hours_per_day * len(work_days.split(',')),
                    "utilization_percentage": 0
                },
                "schedule": {},
                "unassigned_tasks": []
            }
        
        # Parse work days
        work_days_list = [day.strip() for day in work_days.split(',')]
        
        # Organize tasks using AI
        organized_schedule = ai_service.organize_tasks(
            tasks=issues,
            work_hours_per_day=work_hours_per_day,
            work_days=work_days_list
        )
        
        return {
            "username": username,
            "work_constraints": {
                "hours_per_day": work_hours_per_day,
                "work_days": work_days_list
            },
            **organized_schedule
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error organizing tasks: {str(e)}")

@router.post("/organize-tasks-with-meetings")
async def organize_tasks_with_meetings(
    username: str = Query(..., description="Username to organize tasks for"),
    openai_api_key: str = Query(..., description="OpenAI API key for task organization"),
    outlook_client_id: str = Query(..., description="Outlook/Microsoft Graph client ID"),
    outlook_client_secret: str = Query(..., description="Outlook/Microsoft Graph client secret"),
    work_hours_per_day: int = Query(8, description="Working hours per day", ge=1, le=24),
    work_days: str = Query("Monday,Tuesday,Wednesday,Thursday,Friday", description="Comma-separated list of work days")
):
    """Organize user tasks using AI with meeting constraints from Outlook calendar"""
    try:
        # Check if Outlook service is available
        if not OUTLOOK_AVAILABLE:
            raise HTTPException(status_code=400, detail="Outlook integration not available. Please install O365 module or use basic mode.")
        
        # Initialize AI service
        global ai_service, outlook_service
        ai_service = AIService(openai_api_key)
        outlook_service = OutlookService(outlook_client_id, outlook_client_secret)
        
        # First check if user exists
        user_exists = jira_service.check_user_exists(username)
        if not user_exists:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in Jira")
        
        # Authenticate with Outlook
        if not outlook_service.authenticate():
            raise HTTPException(status_code=400, detail="Failed to authenticate with Outlook calendar")
        
        # Get user issues
        issues = jira_service.get_user_issues(username)
        
        if not issues:
            return {
                "message": "No tasks found to organize",
                "summary": {
                    "total_tasks": 0,
                    "total_hours": 0,
                    "available_hours": work_hours_per_day * len(work_days.split(',')),
                    "utilization_percentage": 0
                },
                "schedule": {},
                "unassigned_tasks": [],
                "meetings": {}
            }
        
        # Parse work days
        work_days_list = [day.strip() for day in work_days.split(',')]
        
        # Calculate week dates (next Monday to Friday)
        from datetime import datetime, timedelta
        today = datetime.now()
        days_since_monday = today.weekday()
        if days_since_monday == 0:  # Monday
            monday = today
        else:
            monday = today + timedelta(days=7 - days_since_monday)
        friday = monday + timedelta(days=4)
        
        # Get meetings for the week
        meetings_by_day = outlook_service.get_meetings_for_week(monday, friday)
        
        # Calculate available hours after meetings
        available_hours_by_day = outlook_service.calculate_available_hours(
            meetings_by_day, work_hours_per_day
        )
        
        # Get meeting summary
        meeting_summary = outlook_service.get_meeting_summary(meetings_by_day)
        
        # Organize tasks using AI with meeting constraints
        organized_schedule = ai_service.organize_tasks(
            tasks=issues,
            work_hours_per_day=work_hours_per_day,
            work_days=work_days_list,
            available_hours_by_day=available_hours_by_day
        )
        
        return {
            "username": username,
            "work_constraints": {
                "hours_per_day": work_hours_per_day,
                "work_days": work_days_list,
                "available_hours_by_day": available_hours_by_day
            },
            "meeting_summary": meeting_summary,
            "meetings_by_day": meetings_by_day,
            **organized_schedule
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error organizing tasks with meetings: {str(e)}")

@router.post("/organize-tasks-with-manual-meetings")
async def organize_tasks_with_manual_meetings(
    username: str = Query(..., description="Username to organize tasks for"),
    openai_api_key: str = Query(..., description="OpenAI API key for task organization"),
    work_hours_per_day: int = Query(8, description="Working hours per day", ge=1, le=24),
    work_days: str = Query("Monday,Tuesday,Wednesday,Thursday,Friday", description="Comma-separated list of work days"),
    manual_meetings: str = Query(..., description="JSON string of manual meetings")
):
    """Organize user tasks using AI with manually entered meeting constraints"""
    try:
        import json
        
        # Initialize AI service
        global ai_service
        ai_service = AIService(openai_api_key)
        
        # First check if user exists
        user_exists = jira_service.check_user_exists(username)
        if not user_exists:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in Jira")
        
        # Get user issues
        issues = jira_service.get_user_issues(username)
        
        if not issues:
            return {
                "message": "No tasks found to organize",
                "summary": {
                    "total_tasks": 0,
                    "total_hours": 0,
                    "available_hours": work_hours_per_day * len(work_days.split(',')),
                    "utilization_percentage": 0
                },
                "schedule": {},
                "unassigned_tasks": [],
                "meetings": {}
            }
        
        # Parse work days
        work_days_list = [day.strip() for day in work_days.split(',')]
        
        # Parse manual meetings
        try:
            meetings_by_day = json.loads(manual_meetings)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid meetings JSON format")
        
        # Calculate available hours after meetings
        available_hours_by_day = {}
        for day in work_days_list:
            day_meetings = meetings_by_day.get(day, [])
            if isinstance(day_meetings, dict):
                day_meetings = [day_meetings]  # Convert single meeting to list
            
            total_meeting_hours = sum(
                meeting.get('duration_hours', 0) 
                for meeting in day_meetings
            )
            available_hours_by_day[day] = max(0, work_hours_per_day - total_meeting_hours)
        
        # Get meeting summary
        total_meetings = sum(len(meetings_by_day.get(day, [])) for day in work_days_list)
        total_meeting_hours = sum(
            sum(meeting.get('duration_hours', 0) for meeting in meetings_by_day.get(day, []))
            for day in work_days_list
        )
        
        meeting_summary = {
            "total_meetings": total_meetings,
            "total_meeting_hours": round(total_meeting_hours, 2),
            "average_meetings_per_day": round(total_meetings / len(work_days_list), 1),
            "average_meeting_hours_per_day": round(total_meeting_hours / len(work_days_list), 2)
        }
        
        # Organize tasks using AI with meeting constraints
        organized_schedule = ai_service.organize_tasks(
            tasks=issues,
            work_hours_per_day=work_hours_per_day,
            work_days=work_days_list,
            available_hours_by_day=available_hours_by_day
        )
        
        return {
            "username": username,
            "work_constraints": {
                "hours_per_day": work_hours_per_day,
                "work_days": work_days_list,
                "available_hours_by_day": available_hours_by_day
            },
            "meeting_summary": meeting_summary,
            "meetings_by_day": meetings_by_day,
            **organized_schedule
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error organizing tasks with manual meetings: {str(e)}") 