# Jira Management Dashboard (JiraAI)

A comprehensive Jira management tool for both managers and developers with sprint reporting, capacity planning, and work log tracking.

## Features

### Manager Level
- Sprint Report Dashboard with burndown charts
- Monthly Report Generator
- Capacity Planning Tool
- Team velocity metrics

### Developer Level
- Work Log Tracker
- Daily Sync-up Helper
- Alert System for missing work logs and due dates
- Personal capacity overview

## Quick Start

### Prerequisites
- Python 3.8+
- Jira account with API access
- Jira API token

### Installation

#### Option 1: Quick Start (Recommended)
```bash
cd Jira-AI-proj
python quick_start.py
```

#### Option 2: Manual Setup

1. **Install dependencies:**
```bash
cd Jira-AI-proj
pip install -r requirements.txt
```

2. **Configure Jira credentials:**
Create a `.env` file in the root directory (copy from `env_example.txt`):
```
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your-api-token
```

3. **Run the application:**
```bash
# Terminal 1 - Start backend
python start_backend.py

# Terminal 2 - Start frontend
python start_frontend.py
```

### Getting Your Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Jira Dashboard")
4. Copy the token and use it in your `.env` file

## Project Structure
```
Jira-AI-proj/
├── backend/          # FastAPI backend
├── frontend/         # Streamlit frontend
├── database/         # SQLite database
└── README.md
```

## API Documentation
Once the backend is running, visit: http://localhost:8000/docs

## Usage
1. Access the Streamlit app at http://localhost:8501
2. Enter your Jira credentials
3. Navigate between Manager and Developer dashboards
4. View reports, track work logs, and manage capacity

## Development Timeline
- **Phase 1**: Backend setup and Jira integration (4 hours)
- **Phase 2**: Frontend development (4 hours)
- **Phase 3**: Integration and testing (3 hours)
- **Phase 4**: Polish and documentation (1 hour) 