from jira import JIRA
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from ..config import settings

class JiraService:
    def __init__(self, server: str = None, email: str = None, api_token: str = None):
        self.server = server or settings.JIRA_SERVER
        self.email = email or settings.JIRA_EMAIL
        self.api_token = api_token or settings.JIRA_API_TOKEN
        self.jira = None
        
    def connect(self):
        """Connect to Jira using credentials"""
        try:
            print(f"Attempting to connect to Jira at: {self.server}")
            print(f"Using email: {self.email}")
            
            self.jira = JIRA(
                server=self.server,
                basic_auth=(self.email, self.api_token)
            )
            
            # Test the connection by getting current user info
            try:
                myself = self.jira.myself()
                # myself() returns a dictionary, not an object
                if isinstance(myself, dict):
                    display_name = myself.get('displayName', 'Unknown User')
                    print(f"Successfully connected to Jira as: {display_name}")
                else:
                    display_name = getattr(myself, 'displayName', 'Unknown User')
                    print(f"Successfully connected to Jira as: {display_name}")
                return True
            except Exception as auth_error:
                print(f"Authentication failed: {auth_error}")
                return False
                
        except Exception as e:
            print(f"Failed to connect to Jira: {e}")
            return False
    
    def check_user_exists(self, username: str) -> bool:
        """Check if a user exists in Jira"""
        if not self.jira:
            return False
        
        try:
            # Try to search for issues assigned to the user
            jql = f'assignee = "{username}"'
            print(f"Checking if user exists with JQL: {jql}")
            
            issues = self.jira.search_issues(jql, maxResults=1)
            
            # If we can search without error, the user exists
            print(f"User '{username}' exists in Jira")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Error checking user '{username}': {e}")
            
            # Check for specific error messages that indicate user doesn't exist
            if any(phrase in error_msg for phrase in [
                "does not exist", 
                "not found", 
                "invalid user", 
                "user not found",
                "no user found"
            ]):
                print(f"User '{username}' not found in Jira")
                return False
            
            # For other errors (like permission issues), we'll assume the user exists
            print(f"Assuming user '{username}' exists (error might be permission-related)")
            return True
    
    def get_active_sprints(self) -> List[Dict]:
        """Get all active sprints"""
        if not self.jira:
            return []
        
        try:
            # Get all boards
            boards = self.jira.boards()
            sprints = []
            
            for board in boards:
                try:
                    # Check if board supports sprints by trying to get active sprints
                    active_sprints = self.jira.sprints(board.id, state='active')
                    sprints.extend(active_sprints)
                except Exception as e:
                    # Board doesn't support sprints, skip it silently
                    continue
            
            result = []
            for sprint in sprints:
                try:
                    sprint_data = {
                        'id': sprint.id,
                        'name': sprint.name,
                        'state': sprint.state,
                        'startDate': getattr(sprint, 'startDate', None),
                        'endDate': getattr(sprint, 'endDate', None),
                        'goal': getattr(sprint, 'goal', '')
                    }
                    result.append(sprint_data)
                except Exception as e:
                    print(f"Error processing sprint {getattr(sprint, 'id', 'unknown')}: {e}")
                    continue
            return result
        except Exception as e:
            print(f"Error fetching sprints: {e}")
            return []
    
    def get_sprint_issues(self, sprint_id: int) -> List[Dict]:
        """Get all issues in a sprint"""
        if not self.jira:
            return []
        
        try:
            sprint = self.jira.sprint(sprint_id)
            issues = self.jira.search_issues(
                f'sprint = {sprint_id}',
                expand='changelog,worklog'
            )
            
            result = []
            for issue in issues:
                try:
                    # Get time tracking information
                    time_tracking = getattr(issue.fields, 'timetracking', None)
                    original_estimate = None
                    remaining_estimate = None
                    time_spent = None
                    
                    if time_tracking:
                        original_estimate = getattr(time_tracking, 'originalEstimateSeconds', None)
                        remaining_estimate = getattr(time_tracking, 'remainingEstimateSeconds', None)
                        time_spent = getattr(time_tracking, 'timeSpentSeconds', None)
                    
                    # Convert seconds to hours for display
                    def seconds_to_hours(seconds):
                        if seconds:
                            return round(seconds / 3600, 1)
                        return None
                    
                    # Try multiple common story point field names
                    story_points = None
                    story_point_fields = [
                        'customfield_10016',  # Common story points field
                        'customfield_10008',  # Another common story points field
                        'customfield_10004',  # Yet another common story points field
                        'customfield_10002',  # Alternative story points field
                    ]
                    
                    for field_name in story_point_fields:
                        story_points = getattr(issue.fields, field_name, None)
                        if story_points is not None:
                            break
                    
                    result.append({
                        'key': issue.key,
                        'summary': issue.fields.summary,
                        'description': getattr(issue.fields, 'description', ''),
                        'issue_type': issue.fields.issuetype.name,
                        'status': issue.fields.status.name,
                        'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                        'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                        'reporter': issue.fields.reporter.displayName,
                        'story_points': self._get_story_points(issue),
                        'created': issue.fields.created,
                        'updated': issue.fields.updated,
                        'due_date': getattr(issue.fields, 'duedate', None),
                        'original_estimate_hours': seconds_to_hours(original_estimate),
                        'remaining_estimate_hours': seconds_to_hours(remaining_estimate),
                        'time_spent_hours': seconds_to_hours(time_spent)
                    })
                except Exception as e:
                    print(f"Error processing issue {issue.key}: {e}")
                    continue
            
            return result
        except Exception as e:
            print(f"Error fetching sprint issues: {e}")
            return []
    
    def get_user_worklogs(self, username: str, period: str = "7d") -> List[Dict]:
        """Get work logs for a user in the specified time period
        
        Args:
            username: Jira username/email
            period: Time period string (e.g., "7d", "30d", "3m", "6m", "1y", "all")
        """
        if not self.jira:
            return []
        
        try:
            # Build JQL based on time period
            if period == "all":
                jql = f'worklogAuthor = "{username}" ORDER BY updated DESC'
            else:
                # Parse period string (e.g., "7d", "30d", "3m", "6m", "1y")
                if period.endswith('d'):
                    days = int(period[:-1])
                    jql = f'worklogAuthor = "{username}" AND worklogDate >= startOfDay("-{days}d") ORDER BY updated DESC'
                elif period.endswith('m'):
                    months = int(period[:-1])
                    jql = f'worklogAuthor = "{username}" AND worklogDate >= startOfMonth("-{months}") ORDER BY updated DESC'
                elif period.endswith('y'):
                    years = int(period[:-1])
                    jql = f'worklogAuthor = "{username}" AND worklogDate >= startOfYear("-{years}") ORDER BY updated DESC'
                else:
                    # Default to 7 days if invalid format
                    jql = f'worklogAuthor = "{username}" AND worklogDate >= startOfDay("-7d") ORDER BY updated DESC'
            
            print(f"Searching worklogs with JQL: {jql}")
            
            # Use REST API directly for better worklog retrieval
            url = f"{self.server}/rest/api/2/search"
            params = {
                'jql': jql,
                'fields': 'worklog,summary',
                'expand': 'worklog',
                'maxResults': 100
            }
            
            response = self.jira._session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            issues = data.get('issues', [])
            worklogs = []
            
            print(f"Found {len(issues)} issues with worklogs")
            
            for issue in issues:
                try:
                    issue_key = issue['key']
                    issue_summary = issue['fields']['summary']
                    
                    # Get worklogs from the issue
                    if 'worklog' in issue['fields'] and 'worklogs' in issue['fields']['worklog']:
                         for worklog in issue['fields']['worklog']['worklogs']:
                             # Check if the worklog author matches the username
                             worklog_author = worklog['author']['displayName']
                             worklog_author_name = worklog['author'].get('name', '')
                             worklog_author_email = worklog['author'].get('emailAddress', '')
                             
                             # Match against username, email, or display name
                             if (worklog_author_name == username or 
                                 worklog_author_email == username or 
                                 worklog_author == username or
                                 username in worklog_author_name or
                                 username in worklog_author_email):
                                 
                                 worklogs.append({
                                     'id': worklog['id'],
                                     'issue_key': issue_key,
                                     'issue_summary': issue_summary,
                                     'author': worklog_author,
                                     'comment': worklog.get('comment', ''),
                                     'time_spent_seconds': worklog['timeSpentSeconds'],
                                     'time_spent': worklog['timeSpent'],
                                     'started': worklog['started'],
                                     'created': worklog['created']
                                 })
                                 
                                 # Debug: Print first few worklogs
                                 if len(worklogs) <= 3:
                                     print(f"DEBUG: Found worklog for {username}")
                                     print(f"  Issue: {issue_key}")
                                     print(f"  Author: {worklog_author}")
                                     print(f"  Time: {worklog['timeSpent']}")
                                     print(f"  Started: {worklog['started']}")
                                     print(f"  Comment: {worklog.get('comment', '')[:50]}...")
                
                except Exception as e:
                    print(f"Error processing worklog for issue {issue_key}: {e}")
                    continue
            
            print(f"Found {len(worklogs)} worklogs for user {username}")
            return worklogs
            
        except Exception as e:
            print(f"Error fetching work logs: {e}")
            return []
    
    def get_user_issues(self, username: str) -> List[Dict]:
        """Get all issues assigned to a user"""
        if not self.jira:
            return []
        
        try:
            jql = f'assignee = "{username}" AND status != CLOSED ORDER BY priority DESC'
            print(f"Searching user issues with JQL: {jql}")
            
            issues = self.jira.search_issues(jql, maxResults=100)
            
            result = []
            for issue in issues:
                try:
                    # Get time tracking information
                    time_tracking = getattr(issue.fields, 'timetracking', None)
                    original_estimate = None
                    remaining_estimate = None
                    time_spent = None
                    
                    if time_tracking:
                        original_estimate = getattr(time_tracking, 'originalEstimateSeconds', None)
                        remaining_estimate = getattr(time_tracking, 'remainingEstimateSeconds', None)
                        time_spent = getattr(time_tracking, 'timeSpentSeconds', None)
                    
                    # Convert seconds to hours for display
                    def seconds_to_hours(seconds):
                        if seconds:
                            return round(seconds / 3600, 1)
                        return None
                    
                    # Try multiple common story point field names
                    story_points = None
                    story_point_fields = [
                        'customfield_10016',  # Common story points field
                        'customfield_10008',  # Another common story points field
                        'customfield_10004',  # Yet another common story points field
                        'customfield_10002',  # Alternative story points field
                    ]
                    
                    for field_name in story_point_fields:
                        story_points = getattr(issue.fields, field_name, None)
                        if story_points is not None:
                            break
                    
                    result.append({
                        'key': issue.key,
                        'summary': issue.fields.summary,
                        'status': issue.fields.status.name,
                        'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                        'due_date': getattr(issue.fields, 'duedate', None),
                        'story_points': self._get_story_points(issue),
                        'original_estimate_hours': seconds_to_hours(original_estimate),
                        'remaining_estimate_hours': seconds_to_hours(remaining_estimate),
                        'time_spent_hours': seconds_to_hours(time_spent)
                    })
                except Exception as e:
                    print(f"Error processing issue {issue.key}: {e}")
                    continue
            
            print(f"Found {len(result)} issues for user {username}")
            return result
            
        except Exception as e:
            print(f"Error fetching user issues for {username}: {e}")
            return []
    
    def get_sprint_burndown(self, sprint_id: int) -> Dict:
        """Get burndown data for a sprint"""
        if not self.jira:
            return {}
        
        try:
            sprint = self.jira.sprint(sprint_id)
            issues = self.get_sprint_issues(sprint_id)
            
            total_points = sum(
                issue.get('story_points', 0) or 0 
                for issue in issues 
                if issue.get('story_points')
            )
            
            completed_points = sum(
                issue.get('story_points', 0) or 0 
                for issue in issues 
                if issue.get('story_points') and issue.get('status') == 'CLOSED'
            )
            
            return {
                'total_points': total_points,
                'completed_points': completed_points,
                'remaining_points': total_points - completed_points,
                'completion_percentage': (completed_points / total_points * 100) if total_points > 0 else 0
            }
        except Exception as e:
            print(f"Error calculating burndown: {e}")
            return {}
    
    def get_team_capacity(self, team_members: List[str], sprint_id: int = None) -> Dict:
        """Get capacity information for team members"""
        if not self.jira:
            return {}
        
        capacity_data = {}
        
        for member in team_members:
            try:
                if sprint_id:
                    # Get issues from specific sprint
                    issues = self.get_sprint_issues(sprint_id)
                    # Filter by assignee - match by display name or email
                    member_issues = []
                    for issue in issues:
                        assignee = issue.get('assignee', '')
                        if self._match_assignee(member, assignee):
                            member_issues.append(issue)
                else:
                    # Get all assigned issues
                    issues = self.get_user_issues(member)
                    member_issues = issues
                
                total_points = sum(
                    issue.get('story_points', 0) or 0 
                    for issue in member_issues 
                    if issue.get('story_points')
                )
                
                capacity_data[member] = {
                    'total_issues': len(member_issues),
                    'total_points': total_points,
                    'issues': member_issues
                }
            except Exception as e:
                print(f"Error getting capacity for {member}: {e}")
                capacity_data[member] = {'total_issues': 0, 'total_points': 0, 'issues': []}
        
        return capacity_data
    
    def _match_assignee(self, username: str, assignee: str) -> bool:
        """Helper method to match username with assignee display name"""
        if not assignee or assignee == 'Unassigned':
            return False
        
        # Try exact match first
        if assignee == username:
            return True
        
        # Extract name part from username (before @)
        if '@' in username:
            name_part = username.split('@')[0]
            
            # Try matching by name part in display name
            # e.g., "parvesh.thapa" should match "Parvesh Thapa (Contractor)"
            if name_part.lower() in assignee.lower():
                return True
            
            # Try matching by first name (before dot)
            if '.' in name_part:
                first_name = name_part.split('.')[0]
                if first_name.lower() in assignee.lower():
                    return True
            
            # Try matching by last name (after dot)
            if '.' in name_part:
                last_name = name_part.split('.')[1]
                if last_name.lower() in assignee.lower():
                    return True
            
            # Special case for "mkumar" -> "Manish Kumar"
            if name_part == "mkumar" and "manish" in assignee.lower() and "kumar" in assignee.lower():
                return True
        
        return False
    
    def get_team_capacity_multiple_sprints(self, team_members: List[str], sprint_ids: List[int]) -> Dict:
        """Get capacity information for team members across multiple sprints"""
        if not self.jira:
            return {}
        
        capacity_data = {}
        
        for member in team_members:
            try:
                # Get issues from all specified sprints
                all_member_issues = []
                seen_issues = set()  # Track seen issue keys to avoid duplicates
                
                for sprint_id in sprint_ids:
                    sprint_issues = self.get_sprint_issues(sprint_id)
                    # Filter by assignee
                    for issue in sprint_issues:
                        if self._match_assignee(member, issue.get('assignee', '')):
                            issue_key = issue.get('key', '')
                            
                            # Only add if we haven't seen this issue before
                            if issue_key not in seen_issues:
                                seen_issues.add(issue_key)
                                # Add sprint info to issue
                                issue_with_sprint = issue.copy()
                                issue_with_sprint['sprint_id'] = sprint_id
                                all_member_issues.append(issue_with_sprint)
                            else:
                                # Issue already exists, just add this sprint to the sprint_ids list
                                for existing_issue in all_member_issues:
                                    if existing_issue.get('key') == issue_key:
                                        # If sprint_id is not already in the list, add it
                                        if 'sprint_ids' not in existing_issue:
                                            existing_issue['sprint_ids'] = [existing_issue.get('sprint_id')]
                                        if sprint_id not in existing_issue['sprint_ids']:
                                            existing_issue['sprint_ids'].append(sprint_id)
                                        break
                
                total_points = sum(
                    issue.get('story_points', 0) or 0 
                    for issue in all_member_issues 
                    if issue.get('story_points')
                )
                
                capacity_data[member] = {
                    'total_issues': len(all_member_issues),
                    'total_points': total_points,
                    'issues': all_member_issues
                }
            except Exception as e:
                print(f"Error getting capacity for {member}: {e}")
                capacity_data[member] = {'total_issues': 0, 'total_points': 0, 'issues': []}
        
        return capacity_data
    
    def _get_story_points(self, issue) -> float:
        """Helper method to get story points from an issue using multiple field names"""
        story_point_fields = [
            'customfield_10016',  # Common story points field
            'customfield_10008',  # Another common story points field
            'customfield_10004',  # Yet another common story points field
            'customfield_10002',  # Alternative story points field
        ]
        
        for field_name in story_point_fields:
            story_points = getattr(issue.fields, field_name, None)
            if story_points is not None:
                return story_points or 0
        return 0
    
    def get_monthly_report(self, month: int, year: int) -> Dict:
        """Generate monthly report with real JQL queries"""
        if not self.jira:
            return {}
        
        try:
            # Build date range for the month
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"
            
            print(f"Generating monthly report for {year}-{month:02d}")
            print(f"Date range: {start_date} to {end_date}")
            
            # JQL for issues created in the month
            created_jql = f'created >= "{start_date}" AND created < "{end_date}" ORDER BY created DESC'
            print(f"Created JQL: {created_jql}")
            
            # JQL for issues resolved in the month
            resolved_jql = f'resolved >= "{start_date}" AND resolved < "{end_date}" ORDER BY resolved DESC'
            print(f"Resolved JQL: {resolved_jql}")
            
            # Get issues created
            created_issues = self.jira.search_issues(created_jql, maxResults=1000)
            print(f"Found {len(created_issues)} issues created")
            
            # Get issues resolved
            resolved_issues = self.jira.search_issues(resolved_jql, maxResults=1000)
            print(f"Found {len(resolved_issues)} issues resolved")
            
            # Calculate story points
            total_created_points = sum(
                self._get_story_points(issue) 
                for issue in created_issues
            )
            
            total_resolved_points = sum(
                self._get_story_points(issue) 
                for issue in resolved_issues
            )
            
            # Calculate team velocity (resolved points)
            team_velocity = total_resolved_points
            
            return {
                "period": f"{year}-{month:02d}",
                "summary": {
                    "total_issues_created": len(created_issues),
                    "total_issues_completed": len(resolved_issues),
                    "total_story_points": total_created_points,
                    "team_velocity": team_velocity
                },
                "details": {
                    "created_issues": [
                        {
                            "key": issue.key,
                            "summary": issue.fields.summary,
                            "status": issue.fields.status.name,
                            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                            "story_points": self._get_story_points(issue),
                            "created": issue.fields.created
                        }
                        for issue in created_issues[:10]  # Top 10
                    ],
                    "resolved_issues": [
                        {
                            "key": issue.key,
                            "summary": issue.fields.summary,
                            "status": issue.fields.status.name,
                            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                            "story_points": self._get_story_points(issue),
                            "resolved": issue.fields.resolutiondate
                        }
                        for issue in resolved_issues[:10]  # Top 10
                    ]
                }
            }
            
        except Exception as e:
            print(f"Error generating monthly report: {e}")
            return {
                "period": f"{year}-{month:02d}",
                "summary": {
                    "total_issues_created": 0,
                    "total_issues_completed": 0,
                    "total_story_points": 0,
                    "team_velocity": 0
                },
                "details": {
                    "created_issues": [],
                    "resolved_issues": []
                }
            } 