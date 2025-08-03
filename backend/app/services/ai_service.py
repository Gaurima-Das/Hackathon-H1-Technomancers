import openai
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta

class AIService:
    def __init__(self, api_key: str):
        """Initialize AI service with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
    
    def organize_tasks(self, tasks: List[Dict], work_hours_per_day: int = 8, work_days: List[str] = None, available_hours_by_day: Dict = None) -> Dict:
        """
        Organize tasks using ChatGPT based on priority and time allocation
        
        Args:
            tasks: List of task dictionaries with keys like 'key', 'summary', 'priority', 'remaining_estimate_hours', etc.
            work_hours_per_day: Number of working hours per day (default: 8)
            work_days: List of working days (default: Monday to Friday)
            available_hours_by_day: Dictionary with available hours for each day (after subtracting meetings)
        
        Returns:
            Dictionary with organized task schedule
        """
        if work_days is None:
            work_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # Use available hours if provided, otherwise use full work hours
        if available_hours_by_day is None:
            available_hours_by_day = {day: work_hours_per_day for day in work_days}
        
        # Prepare task data for AI
        task_data = []
        for task in tasks:
            task_info = {
                'key': task.get('key', ''),
                'summary': task.get('summary', ''),
                'priority': task.get('priority', 'Medium'),
                'remaining_hours': task.get('remaining_estimate_hours', 0) or 0,
                'story_points': task.get('story_points', 0) or 0,
                'status': task.get('status', ''),
                'due_date': task.get('due_date', '')
            }
            task_data.append(task_info)
        
        # Create prompt for ChatGPT
        prompt = self._create_organization_prompt(task_data, work_hours_per_day, work_days, available_hours_by_day)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional project manager and task organizer. You help developers organize their tasks efficiently based on priority, time estimates, and work constraints including existing meetings."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, task_data, work_hours_per_day, work_days, available_hours_by_day)
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._fallback_organization(task_data, work_hours_per_day, work_days, available_hours_by_day)
    
    def _create_organization_prompt(self, tasks: List[Dict], work_hours_per_day: int, work_days: List[str], available_hours_by_day: Dict = None) -> str:
        """Create a detailed prompt for task organization"""
        
        # Use available hours if provided, otherwise use full work hours
        if available_hours_by_day is None:
            available_hours_by_day = {day: work_hours_per_day for day in work_days}
        
        # Calculate total available time
        total_available_hours = sum(available_hours_by_day.values())
        total_task_hours = sum(task.get('remaining_hours', 0) for task in tasks)
        
        # Create meeting information for the prompt
        meeting_info = ""
        if available_hours_by_day != {day: work_hours_per_day for day in work_days}:
            meeting_info = "\nMEETING CONSTRAINTS (Available hours after meetings):\n"
            for day in work_days:
                available = available_hours_by_day.get(day, work_hours_per_day)
                if available < work_hours_per_day:
                    meeting_time = work_hours_per_day - available
                    meeting_info += f"- {day}: {available}h available (meetings: {meeting_time}h)\n"
                else:
                    meeting_info += f"- {day}: {available}h available\n"
        
        prompt = f"""
Please organize the following tasks for a developer working {work_hours_per_day} hours per day, {', '.join(work_days)}.

CRITICAL WORKING CONSTRAINTS:
- MAXIMUM {work_hours_per_day} hours per day - NEVER exceed this limit
- Working days: {', '.join(work_days)}
- Total available time: {total_available_hours} hours (after meetings)
- Total task time required: {total_task_hours} hours{meeting_info}

IMPORTANT RULES:
1. NEVER schedule more than the available hours for each day
2. Respect meeting time - only schedule tasks in available hours
3. If a task is too large for one day, split it across multiple days
4. Example: If a task needs 8 hours and only 2 hours remain today, schedule 2 hours today and 6 hours tomorrow
5. Prioritize by importance (High > Medium > Low priority)
6. Consider due dates - urgent tasks should be scheduled earlier
7. Balance workload across days
8. Leave some buffer time for unexpected issues

TASKS TO ORGANIZE:
"""
        
        for i, task in enumerate(tasks, 1):
            prompt += f"""
{i}. {task['key']} - {task['summary']}
   - Priority: {task['priority']}
   - Remaining Hours: {task['remaining_hours']}
   - Story Points: {task['story_points']}
   - Status: {task['status']}
   - Due Date: {task['due_date']}
"""
        
        prompt += f"""

ORGANIZATION REQUIREMENTS:
1. NEVER exceed available hours for each day
2. Split large tasks across multiple days if needed
3. Prioritize tasks by importance (High > Medium > Low priority)
4. Consider due dates - urgent tasks should be scheduled earlier
5. Balance workload across days
6. Group related tasks together when possible
7. Leave some buffer time for unexpected issues

Please provide your response in the following JSON format:
{{
    "summary": {{
        "total_tasks": {len(tasks)},
        "total_hours": {total_task_hours},
        "available_hours": {total_available_hours},
        "utilization_percentage": 0,
        "recommendations": []
    }},
    "schedule": {{
        "Monday": [
            {{
                "task_key": "TASK-123",
                "task_summary": "Task description",
                "allocated_hours": 4,
                "priority": "High",
                "reason": "High priority task with urgent due date"
            }}
        ],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": []
    }},
    "unassigned_tasks": [
        {{
            "task_key": "TASK-456",
            "reason": "Not enough time available"
        }}
    ]
}}

CRITICAL: Ensure no single day exceeds the available hours. Split tasks across days if necessary.
"""
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str, tasks: List[Dict], work_hours_per_day: int, work_days: List[str], available_hours_by_day: Dict = None) -> Dict:
        """Parse the AI response and validate the schedule"""
        try:
            # Try to extract JSON from the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = ai_response[start_idx:end_idx]
            parsed_response = json.loads(json_str)
            
            # Validate and enhance the response
            return self._validate_and_enhance_schedule(parsed_response, tasks, work_hours_per_day, work_days, available_hours_by_day)
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            print(f"Raw response: {ai_response}")
            return self._fallback_organization(tasks, work_hours_per_day, work_days, available_hours_by_day)
    
    def _validate_and_enhance_schedule(self, parsed_response: Dict, tasks: List[Dict], work_hours_per_day: int, work_days: List[str], available_hours_by_day: Dict = None) -> Dict:
        """Validate and enhance the AI-generated schedule"""
        
        # Use available hours if provided, otherwise use full work hours
        if available_hours_by_day is None:
            available_hours_by_day = {day: work_hours_per_day for day in work_days}
        
        # Ensure all required fields exist
        if 'summary' not in parsed_response:
            parsed_response['summary'] = {}
        
        if 'schedule' not in parsed_response:
            parsed_response['schedule'] = {}
        
        if 'unassigned_tasks' not in parsed_response:
            parsed_response['unassigned_tasks'] = []
        
        # Initialize schedule for all work days
        for day in work_days:
            if day not in parsed_response['schedule']:
                parsed_response['schedule'][day] = []
        
        # Validate daily hour limits and fix if needed
        for day in work_days:
            day_schedule = parsed_response['schedule'].get(day, [])
            total_day_hours = sum(task.get('allocated_hours', 0) for task in day_schedule)
            available_hours = available_hours_by_day.get(day, work_hours_per_day)
            
            if total_day_hours > available_hours:
                # Day exceeds limit, need to redistribute
                print(f"Warning: {day} exceeds {available_hours}h limit ({total_day_hours}h). Redistributing...")
                
                # Reset the schedule and use fallback for this day
                parsed_response['schedule'][day] = []
                
                # Find tasks that were scheduled for this day
                day_tasks = []
                for task in tasks:
                    for scheduled_task in day_schedule:
                        if scheduled_task.get('task_key') == task.get('key'):
                            day_tasks.append(task)
                            break
                
                # Redistribute using fallback logic for this day
                current_day_hours = 0
                for task in day_tasks:
                    remaining_hours = task.get('remaining_hours', 0)
                    available_hours_today = available_hours - current_day_hours
                    
                    if available_hours_today > 0:
                        hours_to_allocate = min(remaining_hours, available_hours_today)
                        
                        parsed_response['schedule'][day].append({
                            'task_key': task['key'],
                            'task_summary': task['summary'],
                            'allocated_hours': hours_to_allocate,
                            'priority': task['priority'],
                            'reason': f"Redistributed: {hours_to_allocate}h allocated"
                        })
                        
                        current_day_hours += hours_to_allocate
        
        # Calculate utilization
        total_allocated_hours = 0
        for day_schedule in parsed_response['schedule'].values():
            for task in day_schedule:
                total_allocated_hours += task.get('allocated_hours', 0)
        
        total_available_hours = sum(available_hours_by_day.values())
        utilization = (total_allocated_hours / total_available_hours * 100) if total_available_hours > 0 else 0
        
        parsed_response['summary']['utilization_percentage'] = round(utilization, 1)
        parsed_response['summary']['total_allocated_hours'] = total_allocated_hours
        
        return parsed_response
    
    def _fallback_organization(self, tasks: List[Dict], work_hours_per_day: int, work_days: List[str], available_hours_by_day: Dict = None) -> Dict:
        """Fallback organization when AI fails"""
        
        # Use available hours if provided, otherwise use full work hours
        if available_hours_by_day is None:
            available_hours_by_day = {day: work_hours_per_day for day in work_days}
        
        # Sort tasks by priority and due date
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        sorted_tasks = sorted(tasks, key=lambda x: (
            priority_order.get(x.get('priority', 'Medium'), 1),
            x.get('due_date', ''),
            x.get('remaining_hours', 0)
        ), reverse=True)
        
        schedule = {day: [] for day in work_days}
        unassigned_tasks = []
        current_day_idx = 0
        current_day_hours = 0
        
        for task in sorted_tasks:
            remaining_hours = task.get('remaining_hours', 0)
            
            # Check if we can fit any part of this task in the current day
            while remaining_hours > 0 and current_day_idx < len(work_days):
                current_day = work_days[current_day_idx]
                available_hours_today = available_hours_by_day.get(current_day, work_hours_per_day) - current_day_hours
                
                if available_hours_today > 0:
                    # Can fit some hours in current day
                    hours_to_allocate = min(remaining_hours, available_hours_today)
                    
                    schedule[current_day].append({
                        'task_key': task['key'],
                        'task_summary': task['summary'],
                        'allocated_hours': hours_to_allocate,
                        'priority': task['priority'],
                        'reason': f"Part of task scheduled in {current_day} ({hours_to_allocate}h)"
                    })
                    
                    current_day_hours += hours_to_allocate
                    remaining_hours -= hours_to_allocate
                    
                    # If current day is full, move to next day
                    if current_day_hours >= available_hours_by_day.get(current_day, work_hours_per_day):
                        current_day_idx += 1
                        current_day_hours = 0
                else:
                    # Current day is full, move to next day
                    current_day_idx += 1
                    current_day_hours = 0
            
            # If we still have remaining hours and no more days, add to unassigned
            if remaining_hours > 0:
                unassigned_tasks.append({
                    'task_key': task['key'],
                    'reason': f'Not enough time available in work week (still needs {remaining_hours}h)'
                })
        
        total_allocated_hours = sum(
            sum(task.get('allocated_hours', 0) for task in day_tasks)
            for day_tasks in schedule.values()
        )
        
        total_available_hours = sum(available_hours_by_day.values())
        
        return {
            'summary': {
                'total_tasks': len(tasks),
                'total_hours': sum(task.get('remaining_hours', 0) for task in tasks),
                'available_hours': total_available_hours,
                'total_allocated_hours': total_allocated_hours,
                'utilization_percentage': round((total_allocated_hours / total_available_hours * 100), 1),
                'recommendations': [
                    'Tasks organized by priority and due date',
                    'Tasks split across multiple days when needed',
                    'Meeting time considered in scheduling',
                    'Fallback algorithm used due to AI service unavailability'
                ]
            },
            'schedule': schedule,
            'unassigned_tasks': unassigned_tasks
        } 