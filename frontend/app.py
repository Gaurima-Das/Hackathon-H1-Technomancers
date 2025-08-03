import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict

# Page configuration
st.set_page_config(
    page_title="Jira Management Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .alert-low {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000/api"

class JiraDashboard:
    def __init__(self):
        self.session_state = st.session_state
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'jira_connected' not in self.session_state:
            self.session_state.jira_connected = False
        if 'jira_credentials' not in self.session_state:
            self.session_state.jira_credentials = {}
        if 'current_user' not in self.session_state:
            self.session_state.current_user = ""
    
    def connect_to_jira(self, server, email, api_token):
        """Connect to Jira API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/connect",
                params={"server": server, "email": email, "api_token": api_token},
                timeout=30  # Increased timeout to 30 seconds
            )
            if response.status_code == 200:
                self.session_state.jira_connected = True
                self.session_state.jira_credentials = {
                    "server": server,
                    "email": email,
                    "api_token": api_token
                }
                return True
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                except:
                    error_detail = response.text
                
                st.error(f"❌ Failed to connect to Jira: {error_detail}")
                st.info("💡 Please check your server URL, email, and API token.")
                return False
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend server. Please make sure the backend is running.")
            return False
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
            return False
    
    def api_request(self, endpoint, params=None, timeout=None, method="GET"):
        """Make API request to backend"""
        try:
            # Set timeout - use provided timeout or default based on endpoint
            if timeout is None:
                timeout = 60 if "sprint" in endpoint or "capacity" in endpoint else 30
            
            if method.upper() == "GET":
                response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(f"{API_BASE_URL}/{endpoint}", params=params, timeout=timeout)
            else:
                st.error(f"❌ Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                st.warning("⚠️ User not found in Jira. Please check the username.")
                return None
            elif response.status_code == 400:
                st.error("❌ Bad request. Please check your input.")
                return None
            elif response.status_code == 500:
                st.error("🔧 Server error. Please try again later.")
                return None
            else:
                st.error(f"❌ API Error: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend server. Please make sure the backend is running.")
            return None
        except Exception as e:
            st.error(f"❌ Request error: {str(e)}")
            return None
    
    def show_connection_page(self):
        """Show Jira connection page"""
        st.markdown('<h1 class="main-header">🔗 Connect to Jira</h1>', unsafe_allow_html=True)
        
        # Check backend connection
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=30)  # Increased timeout to 30 seconds
            if response.status_code == 200:
                st.success("✅ Backend server is running")
            else:
                st.error("❌ Backend server is not responding properly")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend server. Please make sure the backend is running on http://localhost:8000")
            st.info("💡 To start the backend, run: `python start_backend.py`")
            return
        except Exception as e:
            st.error(f"❌ Backend connection error: {str(e)}")
            return
        
        with st.form("jira_connection"):
            st.subheader("Enter your Jira credentials")
            
            server = st.text_input(
                "Jira Server URL",
                value="https://wideorbit.atlassian.net",
                help="Your Jira instance URL"
            )
            
            email = st.text_input(
                "Email",
                help="Your Jira account email"
            )
            
            api_token = st.text_input(
                "API Token",
                type="password",
                help="Your Jira API token (not your password)"
            )
            
            submitted = st.form_submit_button("Connect to Jira")
            
            if submitted:
                if server and email and api_token:
                    if self.connect_to_jira(server, email, api_token):
                        st.success("Successfully connected to Jira!")
                        st.rerun()
                else:
                    st.error("Please fill in all fields.")
    
    def show_manager_dashboard(self):
        """Show manager dashboard"""
        st.markdown('<h1 class="main-header">👨‍💼 Manager Dashboard</h1>', unsafe_allow_html=True)
        
        # Sidebar for navigation
        with st.sidebar:
            st.header("Manager Tools")
            page = st.selectbox(
                "Select View",
                ["Sprint Reports", "Capacity Planning", "Monthly Reports", "Team Overview"]
            )
        
        if page == "Sprint Reports":
            self.show_sprint_reports()
        elif page == "Capacity Planning":
            self.show_capacity_planning()
        elif page == "Monthly Reports":
            self.show_monthly_reports()
        elif page == "Team Overview":
            self.show_team_overview()
    
    def show_developer_dashboard(self):
        """Show developer dashboard"""
        st.markdown('<h1 class="main-header">👨‍💻 Developer Dashboard</h1>', unsafe_allow_html=True)
        
        # Sidebar for navigation
        with st.sidebar:
            st.header("Developer Tools")
            page = st.selectbox(
                "Select View",
                ["My Work", "Work Logs", "Alerts", "Daily Sync-up"]
            )
        
        if page == "My Work":
            self.show_my_work()
        elif page == "Work Logs":
            self.show_work_logs()
        elif page == "Alerts":
            self.show_alerts()
        elif page == "Daily Sync-up":
            self.show_daily_syncup()
    
    def show_sprint_reports(self):
        """Show sprint reports"""
        st.subheader("📊 Sprint Reports")
        
        # Get active sprints
        sprints_data = self.api_request("sprints")
        
        if sprints_data and sprints_data.get("sprints"):
            sprints = sprints_data["sprints"]
            
            # Sprint selector
            selected_sprint = st.selectbox(
                "Select Sprint",
                options=sprints,
                format_func=lambda x: x["name"]
            )
            
            if selected_sprint:
                sprint_id = selected_sprint["id"]
                sprint_report = self.api_request(f"sprint/{sprint_id}/report")
                
                if sprint_report:
                    # Sprint summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Total Issues",
                            sprint_report["summary"]["total_issues"]
                        )
                    
                    with col2:
                        st.metric(
                            "Total Points",
                            sprint_report["summary"]["total_points"]
                        )
                    
                    with col3:
                        st.metric(
                            "Completed Points",
                            sprint_report["summary"]["completed_points"]
                        )
                    
                    with col4:
                        completion_pct = sprint_report["summary"]["completion_percentage"]
                        st.metric(
                            "Completion %",
                            f"{completion_pct:.1f}%"
                        )
                    
                    # Burndown chart
                    st.subheader("Burndown Chart")
                    burndown = sprint_report["burndown"]
                    
                    if burndown:
                        fig = go.Figure()
                        
                        # Ideal burndown line
                        total_points = burndown["total_points"]
                        if total_points > 0:
                            fig.add_trace(go.Scatter(
                                x=[0, 100],
                                y=[total_points, 0],
                                mode='lines',
                                name='Ideal Burndown',
                                line=dict(dash='dash', color='gray')
                            ))
                            
                            # Actual burndown
                            remaining = burndown["remaining_points"]
                            fig.add_trace(go.Scatter(
                                x=[0, 100],
                                y=[total_points, remaining],
                                mode='lines+markers',
                                name='Actual Burndown',
                                line=dict(color='blue')
                            ))
                        
                        fig.update_layout(
                            title="Sprint Burndown",
                            xaxis_title="Sprint Progress (%)",
                            yaxis_title="Remaining Story Points",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Issues table
                    st.subheader("Sprint Issues")
                    if sprint_report["issues"]:
                        df = pd.DataFrame(sprint_report["issues"])
                        
                        # Select columns to display in order
                        display_columns = [
                            "key", "summary", "status", "priority", "assignee", "story_points", 
                            "original_estimate_hours", "remaining_estimate_hours", "time_spent_hours", "due_date"
                        ]
                        
                        # Filter columns that exist in the dataframe
                        available_columns = [col for col in display_columns if col in df.columns]
                        
                        # Rename columns for better display
                        column_mapping = {
                            "key": "Key",
                            "summary": "Summary", 
                            "status": "Status",
                            "priority": "Priority",
                            "assignee": "Assignee",
                            "story_points": "Story Points",
                            "original_estimate_hours": "Original Estimate (h)",
                            "remaining_estimate_hours": "Remaining (h)",
                            "time_spent_hours": "Time Spent (h)",
                            "due_date": "Due Date"
                        }
                        
                        # Select and rename columns
                        display_df = df[available_columns].rename(columns=column_mapping)
                        
                        st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No active sprints found or unable to fetch sprint data.")
    
    def show_capacity_planning(self):
        """Show capacity planning with advanced features"""
        st.subheader("📈 Advanced Capacity Planning")
        
        # Create tabs for different capacity planning features
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔄 Generate Plan", 
            "👥 Resources", 
            "📋 Projects", 
            "📊 Reports", 
            "📈 Forecast"
        ])
        
        with tab1:
            self._show_capacity_planning_generator()
        
        with tab2:
            self._show_resource_management()
        
        with tab3:
            self._show_project_management()
        
        with tab4:
            self._show_report_management()
        
        with tab5:
            self._show_capacity_forecast()
    
    def _show_capacity_planning_generator(self):
        """Show capacity planning generator"""
        st.subheader("Generate Capacity Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now().date(),
                help="Select the start date for capacity planning"
            )
            
            optimization_target = st.selectbox(
                "Optimization Target",
                options=["utilization", "cost", "efficiency"],
                help="Choose the primary optimization goal"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=(datetime.now() + timedelta(days=30)).date(),
                help="Select the end date for capacity planning"
            )
            
            include_historical = st.checkbox(
                "Include Historical Data",
                value=True,
                help="Include historical data in planning calculations"
            )
        
        # Resource type filter
        resource_types = st.multiselect(
            "Resource Types",
            options=["human", "equipment", "facility"],
            default=["human"],
            help="Select resource types to include in planning"
        )
        
        # Generate plan button
        if st.button("🚀 Generate Capacity Plan", type="primary"):
            with st.spinner("🔄 Generating capacity plan..."):
                try:
                    # Prepare request data
                    request_data = {
                        "start_date": f"{start_date}T00:00:00",
                        "end_date": f"{end_date}T23:59:59",
                        "optimization_target": optimization_target,
                        "include_historical": include_historical,
                        "resource_types": resource_types if resource_types else None
                    }
                    
                    # Make API request
                    response = requests.post(
                        f"{API_BASE_URL}/capacity/planning/generate",
                        json=request_data,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        self._display_capacity_plan_results(data)
                    else:
                        st.error(f"❌ Failed to generate plan: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    def _display_capacity_plan_results(self, data):
        """Display capacity planning results"""
        st.success("✅ Capacity plan generated successfully!")
        
        # Summary metrics
        st.subheader("📊 Summary")
        summary = data.get("summary", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Planned Capacity",
                f"{summary.get('total_planned_capacity', 0):.1f} hrs"
            )
        
        with col2:
            st.metric(
                "Capacity Utilization",
                f"{summary.get('capacity_utilization_rate', 0):.1%}"
            )
        
        with col3:
            st.metric(
                "Average Efficiency",
                f"{summary.get('average_efficiency_score', 0):.1%}"
            )
        
        with col4:
            st.metric(
                "Total Cost",
                f"${summary.get('total_cost', 0):,.0f}"
            )
        
        # Recommendations
        recommendations = data.get("recommendations", [])
        if recommendations:
            st.subheader("💡 Recommendations")
            for rec in recommendations:
                st.info(f"• {rec}")
        
        # Plans table
        plans = data.get("plans", [])
        if plans:
            st.subheader("📋 Capacity Plans")
            
            # Convert to DataFrame for better display
            plans_data = []
            for plan in plans:
                plans_data.append({
                    "Resource": plan.get("resource", {}).get("name", "Unknown"),
                    "Project": plan.get("project", {}).get("name", "Unknown"),
                    "Planned Capacity": f"{plan.get('planned_capacity', 0):.1f} hrs",
                    "Utilization": f"{plan.get('utilization_rate', 0):.1%}",
                    "Efficiency": f"{plan.get('efficiency_score', 0):.1%}"
                })
            
            df = pd.DataFrame(plans_data)
            st.dataframe(df, use_container_width=True)
    
    def _show_resource_management(self):
        """Show resource management interface"""
        st.subheader("👥 Resource Management")
        
        # Get existing resources
        try:
            response = requests.get(f"{API_BASE_URL}/capacity/resources")
            if response.status_code == 200:
                resources_data = response.json()
                resources = resources_data.get("resources", [])
            else:
                resources = []
        except:
            resources = []
        
        # Create new resource
        with st.expander("➕ Add New Resource"):
            with st.form("add_resource"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Resource Name")
                    resource_type = st.selectbox("Type", ["human", "equipment", "facility"])
                    capacity = st.number_input("Capacity (hours)", min_value=0.0, value=40.0)
                
                with col2:
                    available_capacity = st.number_input("Available Capacity", min_value=0.0, value=40.0)
                    cost_per_unit = st.number_input("Cost per Unit ($)", min_value=0.0, value=100.0)
                    location = st.text_input("Location")
                
                if st.form_submit_button("Add Resource"):
                    if name:
                        resource_data = {
                            "name": name,
                            "type": resource_type,
                            "capacity": capacity,
                            "available_capacity": available_capacity,
                            "cost_per_unit": cost_per_unit,
                            "location": location
                        }
                        
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/capacity/resources",
                                json=resource_data
                            )
                            if response.status_code == 200:
                                st.success("✅ Resource added successfully!")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to add resource: {response.text}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        # Display existing resources
        if resources:
            st.subheader("📋 Existing Resources")
            
            resources_data = []
            for resource in resources:
                resources_data.append({
                    "ID": resource.get("id"),
                    "Name": resource.get("name"),
                    "Type": resource.get("type"),
                    "Capacity": f"{resource.get('capacity', 0):.1f} hrs",
                    "Available": f"{resource.get('available_capacity', 0):.1f} hrs",
                    "Cost/Unit": f"${resource.get('cost_per_unit', 0):.0f}",
                    "Location": resource.get("location", "N/A")
                })
            
            df = pd.DataFrame(resources_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No resources found. Add some resources to get started!")
    
    def _show_project_management(self):
        """Show project management interface"""
        st.subheader("📋 Project Management")
        
        # Get existing projects
        try:
            response = requests.get(f"{API_BASE_URL}/capacity/projects")
            if response.status_code == 200:
                projects_data = response.json()
                projects = projects_data.get("projects", [])
            else:
                projects = []
        except:
            projects = []
        
        # Create new project
        with st.expander("➕ Add New Project"):
            with st.form("add_project"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Project Name")
                    description = st.text_area("Description")
                    start_date = st.date_input("Start Date", value=datetime.now().date())
                
                with col2:
                    end_date = st.date_input("End Date", value=(datetime.now() + timedelta(days=30)).date())
                    status = st.selectbox("Status", ["planned", "active", "completed", "cancelled"])
                    priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
                    budget = st.number_input("Budget ($)", min_value=0.0, value=10000.0)
                
                if st.form_submit_button("Add Project"):
                    if name:
                        project_data = {
                            "name": name,
                            "description": description,
                            "start_date": f"{start_date}T00:00:00",
                            "end_date": f"{end_date}T23:59:59",
                            "status": status,
                            "priority": priority,
                            "budget": budget,
                            "requirements": {"capacity": 100.0}  # Default requirement
                        }
                        
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/capacity/projects",
                                json=project_data
                            )
                            if response.status_code == 200:
                                st.success("✅ Project added successfully!")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to add project: {response.text}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        # Display existing projects
        if projects:
            st.subheader("📋 Existing Projects")
            
            projects_data = []
            for project in projects:
                projects_data.append({
                    "ID": project.get("id"),
                    "Name": project.get("name"),
                    "Status": project.get("status"),
                    "Priority": project.get("priority"),
                    "Start Date": project.get("start_date", "N/A")[:10] if project.get("start_date") else "N/A",
                    "End Date": project.get("end_date", "N/A")[:10] if project.get("end_date") else "N/A",
                    "Budget": f"${project.get('budget', 0):,.0f}" if project.get('budget') else "N/A"
                })
            
            df = pd.DataFrame(projects_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No projects found. Add some projects to get started!")
    
    def _show_report_management(self):
        """Show report management interface"""
        st.subheader("📊 Report Management")
        
        # Generate new report
        with st.expander("📄 Generate New Report"):
            with st.form("generate_report"):
                col1, col2 = st.columns(2)
                
                with col1:
                    report_type = st.selectbox("Report Type", ["monthly", "quarterly", "annual", "custom"])
                    period_start = st.date_input("Period Start", value=datetime.now().date())
                
                with col2:
                    report_format = st.selectbox("Format", ["pdf", "excel", "html"])
                    period_end = st.date_input("Period End", value=(datetime.now() + timedelta(days=30)).date())
                
                if st.form_submit_button("Generate Report"):
                    report_data = {
                        "report_type": report_type,
                        "period_start": f"{period_start}T00:00:00",
                        "period_end": f"{period_end}T23:59:59",
                        "format": report_format,
                        "include_charts": True,
                        "include_details": True
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/capacity/reports/generate",
                            json=report_data
                        )
                        if response.status_code == 200:
                            st.success("✅ Report generated successfully!")
                        else:
                            st.error(f"❌ Failed to generate report: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Get existing reports
        try:
            response = requests.get(f"{API_BASE_URL}/capacity/reports")
            if response.status_code == 200:
                reports_data = response.json()
                reports = reports_data.get("reports", [])
            else:
                reports = []
        except:
            reports = []
        
        # Display existing reports
        if reports:
            st.subheader("📋 Existing Reports")
            
            reports_data = []
            for report in reports:
                reports_data.append({
                    "ID": report.get("id"),
                    "Title": report.get("title"),
                    "Type": report.get("type"),
                    "Format": report.get("format"),
                    "Status": report.get("status"),
                    "Created": report.get("created_at", "N/A")[:10] if report.get("created_at") else "N/A"
                })
            
            df = pd.DataFrame(reports_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No reports found. Generate some reports to get started!")
    
    def _show_capacity_forecast(self):
        """Show capacity forecasting"""
        st.subheader("📈 Capacity Forecast")
        
        months_ahead = st.slider("Months to Forecast", min_value=1, max_value=24, value=12)
        
        if st.button("🔮 Generate Forecast"):
            with st.spinner("🔄 Generating forecast..."):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/capacity/forecast",
                        params={"months_ahead": months_ahead}
                    )
                    
                    if response.status_code == 200:
                        forecast_data = response.json()
                        self._display_forecast_results(forecast_data)
                    else:
                        st.error(f"❌ Failed to generate forecast: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    def _display_forecast_results(self, forecast_data):
        """Display forecast results"""
        st.success("✅ Forecast generated successfully!")
        
        if forecast_data:
            # Convert to DataFrame for better display
            forecast_list = []
            for period, data in forecast_data.items():
                forecast_list.append({
                    "Period": period,
                    "Predicted Utilization": f"{data.get('predicted_utilization', 0):.1%}",
                    "Confidence Level": f"{data.get('confidence_level', 0):.1%}"
                })
            
            df = pd.DataFrame(forecast_list)
            st.dataframe(df, use_container_width=True)
            
            # Create a simple chart
            if len(forecast_list) > 1:
                chart_data = pd.DataFrame(forecast_list)
                chart_data['Predicted Utilization'] = chart_data['Predicted Utilization'].str.rstrip('%').astype(float) / 100
                
                fig = px.line(
                    chart_data, 
                    x='Period', 
                    y='Predicted Utilization',
                    title='Capacity Utilization Forecast',
                    labels={'Predicted Utilization': 'Utilization Rate', 'Period': 'Time Period'}
                )
                fig.update_layout(yaxis_tickformat='.1%')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No forecast data available. Generate some capacity plans first!")
    
    def show_monthly_reports(self):
        """Show monthly reports"""
        st.subheader("📅 Monthly Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            month = st.selectbox("Month", range(1, 13), datetime.now().month - 1)
        
        with col2:
            year = st.selectbox("Year", range(2020, datetime.now().year + 2), datetime.now().year - 2020)
        
        if st.button("Generate Report"):
            report = self.api_request("reports/monthly", {"month": month, "year": year})
            
            if report:
                st.success(f"Report generated for {report['period']}")
                
                # Report summary
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Issues Created", report["summary"]["total_issues_created"])
                
                with col2:
                    st.metric("Issues Completed", report["summary"]["total_issues_completed"])
                
                with col3:
                    st.metric("Story Points", report["summary"]["total_story_points"])
                
                with col4:
                    st.metric("Team Velocity", report["summary"]["team_velocity"])
    
    def show_team_overview(self):
        """Show team overview"""
        st.subheader("👥 Team Overview")
        st.info("Team overview functionality will be implemented here.")
    
    def show_my_work(self):
        """Show developer's assigned work"""
        st.subheader("📋 My Work")
        
        # Username input
        username = st.text_input("Enter your Jira username")
        
        if username:
            issues_data = self.api_request(f"user/{username}/issues")
            
            if issues_data:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Issues", issues_data["total_issues"])
                
                with col2:
                    st.metric("Total Points", issues_data["total_points"])
                
                with col3:
                    if issues_data["issues"]:
                        high_priority = sum(1 for issue in issues_data["issues"] if issue["priority"] == "High")
                        st.metric("High Priority", high_priority)
                
                # AI Task Organization Section
                st.subheader("🤖 AI Task Organization")
                
                # Organization mode selection
                organization_mode = st.radio(
                    "Select Organization Mode",
                    ["Basic (No Meetings)", "With Calendar Integration", "Manual Meeting Input"],
                    help="Choose how to handle meeting time constraints"
                )
                
                # OpenAI API Key input
                openai_api_key = st.text_input(
                    "OpenAI API Key", 
                    value="",
                    type="password",
                    help="Enter your OpenAI API key for AI-powered task organization"
                )
                
                # Outlook credentials (only show if Outlook mode is selected)
                outlook_client_id = ""
                outlook_client_secret = ""
                
                if organization_mode == "With Outlook Calendar":
                    st.subheader("📅 Outlook Calendar Integration")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        outlook_client_id = st.text_input(
                            "Outlook Client ID",
                            type="password",
                            help="Microsoft Graph Client ID for Outlook calendar access"
                        )
                    
                    with col2:
                        outlook_client_secret = st.text_input(
                            "Outlook Client Secret",
                            type="password",
                            help="Microsoft Graph Client Secret for Outlook calendar access"
                        )
                    
                    st.info("💡 **How to get Outlook credentials:** Register an app in Azure AD and grant Calendar.Read permissions.")
                
                # Manual meeting input section
                elif organization_mode == "Manual Meeting Input":
                    st.subheader("📅 Manual Meeting Input")
                    
                    # Meeting input form
                    with st.form("meeting_input_form"):
                        st.write("**Add your meetings for the week:**")
                        
                        # Create meeting inputs for each day
                        manual_meetings = {}
                        work_days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                        
                        for day in work_days_list:
                            st.write(f"**{day}**")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                start_time = st.time_input(f"Start Time", key=f"start_{day}")
                            with col2:
                                end_time = st.time_input(f"End Time", key=f"end_{day}")
                            with col3:
                                meeting_subject = st.text_input(f"Meeting Subject", key=f"subject_{day}")
                            
                            # Calculate duration
                            if start_time and end_time:
                                start_minutes = start_time.hour * 60 + start_time.minute
                                end_minutes = end_time.hour * 60 + end_time.minute
                                duration_hours = max(0, (end_minutes - start_minutes) / 60)
                                
                                if duration_hours > 0:
                                    manual_meetings[day] = {
                                        'start_time': start_time.strftime('%H:%M'),
                                        'end_time': end_time.strftime('%H:%M'),
                                        'duration_hours': round(duration_hours, 2),
                                        'subject': meeting_subject or f"Meeting on {day}"
                                    }
                        
                        submitted = st.form_submit_button("✅ Confirm Meetings")
                        
                        if submitted:
                            st.session_state.manual_meetings = manual_meetings
                            st.success(f"✅ Added {len(manual_meetings)} meetings for the week!")
                    
                    # Display current manual meetings
                    if hasattr(st.session_state, 'manual_meetings') and st.session_state.manual_meetings:
                        st.subheader("📋 Current Meetings")
                        for day, meeting in st.session_state.manual_meetings.items():
                            st.write(f"**{day}**: {meeting['start_time']} - {meeting['end_time']} ({meeting['duration_hours']}h) - {meeting['subject']}")
                        
                        # Clear meetings button
                        if st.button("🗑️ Clear All Meetings"):
                            del st.session_state.manual_meetings
                            st.rerun()
                
                # Work schedule configuration
                col1, col2 = st.columns(2)
                with col1:
                    work_hours_per_day = st.number_input(
                        "Work Hours per Day", 
                        min_value=1, 
                        max_value=24, 
                        value=8,
                        help="Number of working hours per day"
                    )
                
                with col2:
                    work_days = st.multiselect(
                        "Work Days",
                        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                        default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                        help="Select your working days"
                    )
                
                # Organize tasks button
                if st.button("🤖 Organize Tasks with AI", type="primary"):
                    if openai_api_key and work_days:
                        with st.spinner("🤖 AI is organizing your tasks..."):
                            # Determine which API endpoint to call based on mode
                            if organization_mode == "With Calendar Integration":
                                if not outlook_client_id or not outlook_client_secret:
                                    st.error("❌ Please provide both Outlook Client ID and Client Secret for calendar integration.")
                                    return
                                
                                # Call the organize tasks with meetings API
                                organization_data = self.api_request(
                                    "organize-tasks-with-meetings",
                                    {
                                        "username": username,
                                        "openai_api_key": openai_api_key,
                                        "outlook_client_id": outlook_client_id,
                                        "outlook_client_secret": outlook_client_secret,
                                        "work_hours_per_day": work_hours_per_day,
                                        "work_days": ",".join(work_days)
                                    },
                                    method="POST"
                                )
                            elif organization_mode == "Manual Meeting Input":
                                # Check if manual meetings are available
                                if not hasattr(st.session_state, 'manual_meetings') or not st.session_state.manual_meetings:
                                    st.error("❌ Please add your meetings using the form above before organizing tasks.")
                                    return
                                
                                # Call the organize tasks with manual meetings API
                                organization_data = self.api_request(
                                    "organize-tasks-with-manual-meetings",
                                    {
                                        "username": username,
                                        "openai_api_key": openai_api_key,
                                        "work_hours_per_day": work_hours_per_day,
                                        "work_days": ",".join(work_days),
                                        "manual_meetings": json.dumps(st.session_state.manual_meetings)
                                    },
                                    method="POST"
                                )
                            else:
                                # Call the basic organize tasks API
                                organization_data = self.api_request(
                                    "organize-tasks",
                                    {
                                        "username": username,
                                        "openai_api_key": openai_api_key,
                                        "work_hours_per_day": work_hours_per_day,
                                        "work_days": ",".join(work_days)
                                    },
                                    method="POST"
                                )
                        
                        if organization_data:
                            # Display organization summary
                            st.success("✅ Tasks organized successfully!")
                            
                            # Summary metrics
                            summary = organization_data.get("summary", {})
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Total Tasks", summary.get("total_tasks", 0))
                            
                            with col2:
                                st.metric("Total Hours", summary.get("total_hours", 0))
                            
                            with col3:
                                st.metric("Available Hours", summary.get("available_hours", 0))
                            
                            with col4:
                                st.metric("Utilization %", f"{summary.get('utilization_percentage', 0)}%")
                            
                            # Weekly workload chart
                            st.subheader("📊 Weekly Workload Distribution")
                            
                            # Get schedule data
                            schedule = organization_data.get("schedule", {})
                            
                            # Prepare data for the chart
                            days = list(schedule.keys())
                            hours_per_day = []
                            for day in days:
                                day_hours = sum(task.get('allocated_hours', 0) for task in schedule.get(day, []))
                                hours_per_day.append(day_hours)
                            
                            # Create a simple bar chart using plotly
                            try:
                                import plotly.graph_objects as go
                                
                                fig = go.Figure(data=[
                                    go.Bar(
                                        x=days,
                                        y=hours_per_day,
                                        text=[f"{h}h" for h in hours_per_day],
                                        textposition='auto',
                                        marker_color=['#ff6b6b' if h > work_hours_per_day * 0.9 else '#4ecdc4' if h > work_hours_per_day * 0.7 else '#45b7d1' for h in hours_per_day]
                                    )
                                ])
                                
                                # Add max line based on available hours
                                max_hours = work_hours_per_day
                                if "work_constraints" in organization_data:
                                    available_hours = organization_data["work_constraints"].get("available_hours_by_day", {})
                                    max_hours = max(available_hours.values()) if available_hours else work_hours_per_day
                                
                                fig.add_hline(y=max_hours, line_dash="dash", line_color="red", 
                                            annotation_text=f"Max Available ({max_hours}h)")
                                
                                fig.update_layout(
                                    title="Daily Workload Distribution (After Meetings)",
                                    xaxis_title="Day",
                                    yaxis_title="Hours",
                                    yaxis=dict(range=[0, max_hours * 1.1]),
                                    height=400
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                            except ImportError:
                                # Fallback if plotly is not available
                                st.write("📈 Workload by day:")
                                for day, hours in zip(days, hours_per_day):
                                    utilization = (hours / work_hours_per_day) * 100
                                    st.write(f"{day}: {hours}h ({utilization:.1f}% utilization)")
                            
                            # Display schedule
                            st.subheader("📅 Weekly Schedule")
                            
                            # Calendar view
                            st.subheader("🗓️ Calendar View")
                            
                            # Create calendar layout
                            calendar_cols = st.columns(5)  # 5 work days
                            
                            for i, (day, tasks) in enumerate(schedule.items()):
                                with calendar_cols[i]:
                                    st.markdown(f"### {day}")
                                    
                                    total_day_hours = sum(task.get('allocated_hours', 0) for task in tasks)
                                    
                                    # Day header with total hours
                                    if total_day_hours > 0:
                                        # Get available hours for this day (considering meetings)
                                        available_hours = work_hours_per_day
                                        if "work_constraints" in organization_data:
                                            available_hours = organization_data["work_constraints"].get("available_hours_by_day", {}).get(day, work_hours_per_day)
                                        
                                        st.markdown(f"**{total_day_hours}h / {available_hours}h**")
                                        
                                        # Progress bar for day utilization
                                        utilization = (total_day_hours / available_hours) * 100 if available_hours > 0 else 0
                                        st.progress(min(utilization / 100, 1.0))
                                        
                                        # Color code based on utilization
                                        if utilization > 90:
                                            st.warning("⚠️ High utilization")
                                        elif utilization > 70:
                                            st.info("📊 Good utilization")
                                        else:
                                            st.success("✅ Balanced workload")
                                        
                                        # Show meeting time if any
                                        if available_hours < work_hours_per_day:
                                            meeting_time = work_hours_per_day - available_hours
                                            st.info(f"📅 {meeting_time}h in meetings")
                                    else:
                                        st.info("📭 No tasks scheduled")
                                    
                                    # Display tasks for this day
                                    for task in tasks:
                                        priority_color = {
                                            "High": "🔴",
                                            "Medium": "🟡", 
                                            "Low": "🟢"
                                        }.get(task.get("priority", "Medium"), "⚪")
                                        
                                        # Create task card
                                        with st.container():
                                            st.markdown(f"""
                                            <div style="
                                                border: 1px solid #ddd; 
                                                border-radius: 5px; 
                                                padding: 10px; 
                                                margin: 5px 0; 
                                                background-color: #f9f9f9;
                                            ">
                                                <strong>{priority_color} {task['task_key']}</strong><br>
                                                <small>{task['task_summary'][:50]}{'...' if len(task['task_summary']) > 50 else ''}</small><br>
                                                <strong>⏱️ {task.get('allocated_hours', 0)}h</strong><br>
                                                <small>{task.get('reason', '')[:40]}{'...' if len(task.get('reason', '')) > 40 else ''}</small>
                                            </div>
                                            """, unsafe_allow_html=True)
                            
                            # Detailed schedule view
                            st.subheader("📋 Detailed Schedule")
                            for day, tasks in schedule.items():
                                if tasks:  # Only show days with tasks
                                    with st.expander(f"📅 {day} ({sum(task.get('allocated_hours', 0) for task in tasks)}h)"):
                                        for task in tasks:
                                            priority_color = {
                                                "High": "🔴",
                                                "Medium": "🟡", 
                                                "Low": "🟢"
                                            }.get(task.get("priority", "Medium"), "⚪")
                                            
                                            st.write(f"{priority_color} **{task['task_key']}** - {task['task_summary']}")
                                            st.write(f"   ⏱️ {task.get('allocated_hours', 0)}h | {task.get('reason', '')}")
                            
                            # Display unassigned tasks
                            unassigned_tasks = organization_data.get("unassigned_tasks", [])
                            if unassigned_tasks:
                                st.subheader("⚠️ Unassigned Tasks")
                                for task in unassigned_tasks:
                                    st.write(f"🔴 **{task['task_key']}** - {task.get('reason', 'Not enough time')}")
                            
                            # Display meeting information if available
                            if "meeting_summary" in organization_data:
                                st.subheader("📅 Meeting Summary")
                                meeting_summary = organization_data.get("meeting_summary", {})
                                meetings_by_day = organization_data.get("meetings_by_day", {})
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Meetings", meeting_summary.get("total_meetings", 0))
                                with col2:
                                    st.metric("Meeting Hours", f"{meeting_summary.get('total_meeting_hours', 0)}h")
                                with col3:
                                    st.metric("Avg/Day", f"{meeting_summary.get('average_meetings_per_day', 0)}")
                                with col4:
                                    st.metric("Avg Hours/Day", f"{meeting_summary.get('average_meeting_hours_per_day', 0)}h")
                                
                                # Show available hours after meetings
                                if "work_constraints" in organization_data:
                                    available_hours = organization_data["work_constraints"].get("available_hours_by_day", {})
                                    st.subheader("⏰ Available Hours After Meetings")
                                    
                                    avail_cols = st.columns(5)
                                    for i, (day, hours) in enumerate(available_hours.items()):
                                        with avail_cols[i]:
                                            st.metric(day, f"{hours}h")
                                
                                # Show meetings by day
                                st.subheader("📋 Meetings by Day")
                                for day, meetings in meetings_by_day.items():
                                    if meetings:
                                        with st.expander(f"📅 {day} ({len(meetings)} meetings)"):
                                            for meeting in meetings:
                                                st.write(f"🕐 **{meeting['start_time']} - {meeting['end_time']}** ({meeting['duration_hours']}h)")
                                                st.write(f"📝 {meeting['subject']}")
                                                if meeting.get('location'):
                                                    st.write(f"📍 {meeting['location']}")
                                                if meeting.get('organizer'):
                                                    st.write(f"👤 {meeting['organizer']}")
                                                st.write("---")
                            
                            # Display AI recommendations
                            recommendations = summary.get("recommendations", [])
                            if recommendations:
                                st.subheader("💡 AI Recommendations")
                                for rec in recommendations:
                                    st.write(f"• {rec}")
                            
                            # Export to calendar
                            st.subheader("📅 Export to Calendar")
                            
                            # Generate ICS content
                            ics_content = self._generate_ics_schedule(schedule, username, work_hours_per_day)
                            
                            if ics_content:
                                st.download_button(
                                    label="📥 Download Calendar File (.ics)",
                                    data=ics_content,
                                    file_name=f"jira_tasks_{username}_{datetime.now().strftime('%Y%m%d')}.ics",
                                    mime="text/calendar",
                                    help="Download this file and import it into your calendar application (Google Calendar, Outlook, etc.)"
                                )
                                
                                st.info("💡 **How to use:** Download the .ics file and import it into your calendar application. Each task will appear as a calendar event with the allocated time.")
                        else:
                            st.error("❌ Failed to organize tasks. Please check your API key and try again.")
                    else:
                        st.warning("⚠️ Please provide OpenAI API key and select work days.")
                
                # Original issues table
                st.subheader("📋 All Tasks")
                if issues_data["issues"]:
                    df = pd.DataFrame(issues_data["issues"])
                    
                    # Select columns to display in order
                    display_columns = [
                        "key", "summary", "status", "priority", "story_points", 
                        "original_estimate_hours", "remaining_estimate_hours", "time_spent_hours", "due_date"
                    ]
                    
                    # Filter columns that exist in the dataframe
                    available_columns = [col for col in display_columns if col in df.columns]
                    
                    # Rename columns for better display
                    column_mapping = {
                        "key": "Key",
                        "summary": "Summary", 
                        "status": "Status",
                        "priority": "Priority",
                        "story_points": "Story Points",
                        "original_estimate_hours": "Original Estimate (h)",
                        "remaining_estimate_hours": "Remaining (h)",
                        "time_spent_hours": "Time Spent (h)",
                        "due_date": "Due Date"
                    }
                    
                    # Select and rename columns
                    display_df = df[available_columns].rename(columns=column_mapping)
                    
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.info("📭 No issues found for this user. The user might not have any assigned issues or the username might be incorrect.")
            else:
                st.info("💡 Enter a valid Jira username to see your assigned work.")
    
    def show_work_logs(self):
        """Show work logs"""
        st.subheader("⏱️ Work Logs")
        
        # Username input
        username = st.text_input("Enter your Jira username", value="parvesh.thapa@wideorbit.com")
        
        if username:
            # Time period selector with custom years
            col1, col2 = st.columns(2)
            
            with col1:
                period_options = {
                    "Last 7 Days": "7d",
                    "Last 30 Days": "30d", 
                    "Last 3 Months": "3m",
                    "Last 6 Months": "6m",
                    "Last 1 Year": "1y",
                    "Last 2 Years": "2y",
                    "Last 3 Years": "3y",
                    "All Time": "all"
                }
                
                selected_period = st.selectbox(
                    "Select Time Period",
                    options=list(period_options.keys()),
                    index=0
                )
                
                period = period_options[selected_period]
            
            with col2:
                # Custom year range
                st.write("**Or use custom range:**")
                custom_years = st.number_input("Years back", min_value=1, max_value=10, value=2)
                if st.button("Use Custom Range"):
                    period = f"{custom_years}y"
            
            # Get worklogs for the specified user
            worklogs_data = self.api_request(f"user/{username}/worklogs", {"period": period})
            
            if worklogs_data:
                # Summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Work Logs", worklogs_data["total_worklogs"])
                
                with col2:
                    st.metric("Total Hours", worklogs_data["total_hours"])
                
                with col3:
                    # Calculate average hours based on period
                    if period == "7d":
                        avg_hours = worklogs_data["total_hours"] / 7
                        avg_label = "Avg Hours/Day"
                    elif period == "30d":
                        avg_hours = worklogs_data["total_hours"] / 30
                        avg_label = "Avg Hours/Day"
                    elif period == "3m":
                        avg_hours = worklogs_data["total_hours"] / 90
                        avg_label = "Avg Hours/Day"
                    elif period == "6m":
                        avg_hours = worklogs_data["total_hours"] / 180
                        avg_label = "Avg Hours/Day"
                    elif period == "1y":
                        avg_hours = worklogs_data["total_hours"] / 365
                        avg_label = "Avg Hours/Day"
                    elif period == "2y":
                        avg_hours = worklogs_data["total_hours"] / 730
                        avg_label = "Avg Hours/Day"
                    elif period == "3y":
                        avg_hours = worklogs_data["total_hours"] / 1095
                        avg_label = "Avg Hours/Day"
                    elif period.endswith('y'):
                        years = int(period[:-1])
                        avg_hours = worklogs_data["total_hours"] / (years * 365)
                        avg_label = f"Avg Hours/Day ({years} years)"
                    else:  # all
                        avg_hours = worklogs_data["total_hours"]
                        avg_label = "Total Hours"
                    
                    st.metric(avg_label, f"{avg_hours:.1f}")
                
                # Work logs table
                if worklogs_data["worklogs"]:
                    df = pd.DataFrame(worklogs_data["worklogs"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info(f"📭 No work logs found for {username} in the selected period ({selected_period}).")
            else:
                st.info("💡 Unable to fetch work logs. Please check your username and connection.")
        else:
            st.info("💡 Please enter your Jira username to view work logs.")
    
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
        
        return False
    
    def _generate_ics_schedule(self, schedule: Dict, username: str, work_hours_per_day: int) -> str:
        """Generate ICS calendar file content from task schedule"""
        try:
            from datetime import datetime, timedelta
            
            # Get current date to calculate actual dates for the week
            today = datetime.now()
            
            # Find the next Monday (or today if it's Monday)
            days_since_monday = today.weekday()
            if days_since_monday == 0:  # Monday
                monday = today
            else:
                monday = today + timedelta(days=7 - days_since_monday)
            
            # Create ICS content
            ics_lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Jira AI Task Organizer//EN",
                "CALSCALE:GREGORIAN",
                "METHOD:PUBLISH"
            ]
            
            # Map day names to dates
            day_to_date = {
                "Monday": monday,
                "Tuesday": monday + timedelta(days=1),
                "Wednesday": monday + timedelta(days=2),
                "Thursday": monday + timedelta(days=3),
                "Friday": monday + timedelta(days=4)
            }
            
            # Generate events for each task
            for day_name, tasks in schedule.items():
                if day_name in day_to_date and tasks:
                    day_date = day_to_date[day_name]
                    
                    for task in tasks:
                        task_key = task.get('task_key', '')
                        task_summary = task.get('task_summary', '')
                        allocated_hours = task.get('allocated_hours', 0)
                        priority = task.get('priority', 'Medium')
                        reason = task.get('reason', '')
                        
                        # Create event start time (9 AM by default)
                        start_time = day_date.replace(hour=9, minute=0, second=0, microsecond=0)
                        end_time = start_time + timedelta(hours=allocated_hours)
                        
                        # Format dates for ICS
                        start_str = start_time.strftime("%Y%m%dT%H%M%S")
                        end_str = end_time.strftime("%Y%m%dT%H%M%S")
                        
                        # Create unique ID
                        event_id = f"jira-task-{task_key}-{start_str}"
                        
                        # Priority color mapping
                        priority_colors = {
                            "High": "#ff0000",
                            "Medium": "#ffa500", 
                            "Low": "#00ff00"
                        }
                        color = priority_colors.get(priority, "#0000ff")
                        
                        # Create event
                        event_lines = [
                            "BEGIN:VEVENT",
                            f"UID:{event_id}",
                            f"DTSTART:{start_str}",
                            f"DTEND:{end_str}",
                            f"SUMMARY:[{priority}] {task_key}",
                            f"DESCRIPTION:{task_summary}\\n\\nReason: {reason}\\nAllocated: {allocated_hours}h",
                            f"LOCATION:Jira Task",
                            f"STATUS:CONFIRMED",
                            f"SEQUENCE:0",
                            f"CATEGORIES:Jira,{priority}",
                            f"COLOR:{color}",
                            "END:VEVENT"
                        ]
                        
                        ics_lines.extend(event_lines)
            
            ics_lines.append("END:VCALENDAR")
            
            return "\r\n".join(ics_lines)
            
        except Exception as e:
            print(f"Error generating ICS file: {e}")
            return ""
    
    def show_alerts(self):
        """Show alerts"""
        st.subheader("🚨 Alerts")
        
        # Username input
        username = st.text_input("Enter your Jira username")
        
        if username:
            alerts_data = self.api_request("alerts", {"username": username})
            
            if alerts_data:
                st.metric("Total Alerts", alerts_data["total_alerts"])
                
                if alerts_data["alerts"]:
                    for alert in alerts_data["alerts"]:
                        severity_class = f"alert-{alert['severity']}"
                        st.markdown(f"""
                        <div class="metric-card {severity_class}">
                            <strong>{alert['type'].replace('_', ' ').title()}</strong><br>
                            {alert['message']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ No alerts found! Everything looks good.")
            else:
                st.info("💡 Enter a valid Jira username to check for alerts.")
    
    def show_daily_syncup(self):
        """Show daily sync-up helper"""
        st.subheader("📅 Daily Sync-up Helper")
        
        # Username input
        username = st.text_input("Enter your Jira username", value="parvesh.thapa@wideorbit.com")
        
        if username:
            # Yesterday's work
            st.subheader("Yesterday's Work")
            yesterday_worklogs = self.api_request(f"user/{username}/worklogs", {"period": "1d"})
            
            if yesterday_worklogs and yesterday_worklogs["worklogs"]:
                for worklog in yesterday_worklogs["worklogs"]:
                    st.write(f"✅ {worklog['issue_key']}: {worklog['comment']}")
            elif yesterday_worklogs:
                st.info("📭 No work logs found for yesterday. You might want to log your work.")
            else:
                st.info("💡 Enter a valid Jira username to see yesterday's work.")
            
            # Today's planned work from active sprint
            st.subheader("Today's Planned Work (Active Sprint)")
            
            # Get active sprints
            sprints_data = self.api_request("sprints")
            active_sprint_issues = []
            
            if sprints_data and sprints_data.get("sprints"):
                active_sprints = [sprint for sprint in sprints_data["sprints"] if sprint.get("state") == "active"]
                
                if active_sprints:
                    # Get issues from first active sprint
                    active_sprint = active_sprints[0]
                    sprint_report = self.api_request(f"sprint/{active_sprint['id']}/report")
                    
                    if sprint_report and sprint_report.get("issues"):
                        # Filter issues assigned to the user - match by display name or email
                        user_issues = []
                        for issue in sprint_report["issues"]:
                            assignee = issue.get("assignee", "")
                            if self._match_assignee(username, assignee):
                                user_issues.append(issue)
                        active_sprint_issues = user_issues[:5]  # Show top 5
                        
                        st.write(f"**Active Sprint:** {active_sprint['name']}")
                        
                        if active_sprint_issues:
                            for issue in active_sprint_issues:
                                st.write(f"📋 {issue['key']}: {issue['summary']} ({issue['status']})")
                        else:
                            st.info(f"📭 No issues assigned to you in the active sprint '{active_sprint['name']}'")
                else:
                    st.info("📭 No active sprints found")
            else:
                st.info("💡 Unable to fetch sprint information")
    
    def run(self):
        """Main application runner"""
        self.init_session_state()
        
        # Main navigation
        if not self.session_state.jira_connected:
            self.show_connection_page()
        else:
            # User type selection
            user_type = st.sidebar.selectbox(
                "Select User Type",
                ["Manager", "Developer"]
            )
            
            if user_type == "Manager":
                self.show_manager_dashboard()
            else:
                self.show_developer_dashboard()
            
            # Disconnect button
            if st.sidebar.button("Disconnect from Jira"):
                self.session_state.jira_connected = False
                self.session_state.jira_credentials = {}
                st.rerun()

if __name__ == "__main__":
    dashboard = JiraDashboard()
    dashboard.run() 