# Jira Management Dashboard - Architecture Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Design](#database-design)
7. [API Design](#api-design)
8. [Security Implementation](#security-implementation)
9. [Deployment Architecture](#deployment-architecture)
10. [Development Workflow](#development-workflow)

## Project Overview

The Jira Management Dashboard (JiraAI) is a comprehensive project management tool that provides both manager and developer perspectives for Jira project tracking. It offers sprint reporting, capacity planning, work log tracking, and alert systems.

### Key Features
- **Manager Level**: Sprint reports, burndown charts, capacity planning, team velocity metrics
- **Developer Level**: Work log tracking, daily sync-up helper, alert system, personal capacity overview

## Technology Stack

### Backend Technologies
- **FastAPI** (v0.104.1) - Modern, fast web framework for building APIs
- **Uvicorn** (v0.24.0) - ASGI server for running FastAPI applications
- **SQLAlchemy** (v2.0.23) - SQL toolkit and Object-Relational Mapping (ORM)
- **Pydantic** (v2.5.0) - Data validation using Python type annotations
- **Python-dotenv** (v1.0.0) - Environment variable management

### Frontend Technologies
- **Streamlit** (v1.28.1) - Rapid web application development framework
- **Plotly** (v5.17.0) - Interactive plotting library for charts and graphs
- **Pandas** (v2.1.4) - Data manipulation and analysis
- **Streamlit-option-menu** (v0.3.6) - Custom navigation menu component
- **Streamlit-aggrid** (v0.3.4) - Advanced data grid component
- **Streamlit-authenticator** (v0.2.3) - Authentication components

### External Integrations
- **Jira Python SDK** (v3.5.1) - Official Jira REST API client
- **Requests** (v2.31.0) - HTTP library for API calls

### Database
- **SQLite** - Lightweight, serverless database for local development
- **SQLAlchemy ORM** - Database abstraction layer

### Security & Authentication
- **Python-jose** (v3.3.0) - JWT token handling
- **Passlib** (v1.7.4) - Password hashing and verification
- **Bcrypt** - Password hashing algorithm

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (Streamlit)   │◄──►│   (FastAPI)     │◄──►│   (Jira API)    │
│                 │    │                 │    │                 │
│ - Manager View  │    │ - REST API      │    │ - Issues        │
│ - Developer     │    │ - Jira Service  │    │ - Sprints       │
│   View          │    │ - Database      │    │ - Work Logs     │
│ - Charts        │    │   Operations    │    │ - Users         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite)      │
                       │                 │
                       │ - Sprints       │
                       │ - Issues        │
                       │ - Work Logs     │
                       │ - Users         │
                       │ - Alerts        │
                       └─────────────────┘
```

## Backend Architecture

### Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and setup
│   ├── models.py            # SQLAlchemy data models
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoint definitions
│   └── services/
│       ├── __init__.py
│       └── jira_service.py  # Jira API integration service
└── requirements.txt         # Backend dependencies
```

### Core Components

#### 1. FastAPI Application (`main.py`)
- **Purpose**: Application entry point and configuration
- **Features**:
  - CORS middleware for cross-origin requests
  - API router integration
  - Database table initialization on startup
  - Health check endpoints

#### 2. Configuration Management (`config.py`)
- **Purpose**: Centralized configuration using environment variables
- **Configuration Areas**:
  - Jira server settings (URL, email, API token)
  - Database connection string
  - Security settings (secret keys, token expiration)
  - Email configuration for alerts

#### 3. Database Layer (`database.py`)
- **Purpose**: Database connection management and session handling
- **Features**:
  - SQLAlchemy engine configuration
  - Session factory for database operations
  - Automatic table creation
  - Connection pooling

#### 4. Data Models (`models.py`)
- **Purpose**: SQLAlchemy ORM models for data persistence
- **Models**:
  - `Sprint`: Sprint information and metadata
  - `Issue`: Jira issues with relationships
  - `WorkLog`: Time tracking and work logs
  - `User`: User information and authentication
  - `Alert`: System alerts and notifications

#### 5. Jira Service (`services/jira_service.py`)
- **Purpose**: Jira API integration and data retrieval
- **Key Methods**:
  - `connect()`: Establish Jira connection
  - `get_active_sprints()`: Retrieve active sprints
  - `get_sprint_issues()`: Get issues in a sprint
  - `get_user_worklogs()`: Retrieve user work logs
  - `get_sprint_burndown()`: Calculate burndown metrics
  - `get_team_capacity()`: Team capacity analysis

#### 6. API Routes (`api/routes.py`)
- **Purpose**: REST API endpoint definitions
- **Endpoint Categories**:
  - **Health & Connection**: `/health`, `/connect`
  - **Sprint Management**: `/sprints`, `/sprint/{id}`, `/sprint/{id}/report`
  - **User Operations**: `/user/{username}/worklogs`, `/user/{username}/issues`
  - **Team Management**: `/capacity`
  - **Alerts**: `/alerts`
  - **Reporting**: `/reports/monthly`

## Frontend Architecture

### Directory Structure
```
frontend/
├── app.py                   # Main Streamlit application
└── requirements.txt         # Frontend dependencies
```

### Core Components

#### 1. Streamlit Application (`app.py`)
- **Purpose**: Main frontend application with dual dashboard views
- **Architecture Pattern**: Class-based component architecture

#### 2. JiraDashboard Class
- **Purpose**: Main application controller
- **Key Methods**:
  - `init_session_state()`: Initialize application state
  - `connect_to_jira()`: Handle Jira authentication
  - `api_request()`: Backend API communication
  - `show_manager_dashboard()`: Manager interface
  - `show_developer_dashboard()`: Developer interface

#### 3. Manager Dashboard Features
- **Sprint Reports**: Burndown charts, issue tracking, completion metrics
- **Capacity Planning**: Team member workload analysis
- **Monthly Reports**: Period-based reporting
- **Team Overview**: Team performance metrics

#### 4. Developer Dashboard Features
- **My Work**: Assigned issues and priorities
- **Work Logs**: Time tracking and history
- **Alerts**: Missing work logs, due dates, notifications
- **Daily Sync-up**: Yesterday's work and today's plans

#### 5. UI Components
- **Custom CSS**: Styled components for better UX
- **Plotly Charts**: Interactive burndown and metric visualizations
- **Streamlit Components**: Forms, dataframes, metrics, expanders
- **Responsive Layout**: Wide layout with sidebar navigation

## Database Design

### Entity Relationship Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Sprint    │    │    Issue    │    │  WorkLog    │
│             │    │             │    │             │
│ - id        │◄──►│ - id        │◄──►│ - id        │
│ - jira_id   │    │ - jira_key  │    │ - jira_id   │
│ - name      │    │ - summary   │    │ - issue_id  │
│ - state     │    │ - status    │    │ - author    │
│ - dates     │    │ - assignee  │    │ - time_spent│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │    Alert    │    │             │
│             │    │             │    │             │
│ - id        │◄──►│ - id        │    │             │
│ - username  │    │ - user_id   │    │             │
│ - email     │    │ - alert_type│    │             │
│ - active    │    │ - message   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Table Schemas

#### Sprint Table
```sql
CREATE TABLE sprints (
    id INTEGER PRIMARY KEY,
    jira_id INTEGER UNIQUE,
    name VARCHAR,
    state VARCHAR,
    start_date DATETIME,
    end_date DATETIME,
    goal TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Issue Table
```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    jira_key VARCHAR UNIQUE,
    summary VARCHAR,
    description TEXT,
    issue_type VARCHAR,
    status VARCHAR,
    priority VARCHAR,
    assignee VARCHAR,
    reporter VARCHAR,
    story_points FLOAT,
    created_at DATETIME,
    updated_at DATETIME,
    due_date DATETIME,
    sprint_id INTEGER REFERENCES sprints(id)
);
```

#### WorkLog Table
```sql
CREATE TABLE work_logs (
    id INTEGER PRIMARY KEY,
    jira_id INTEGER UNIQUE,
    issue_id INTEGER REFERENCES issues(id),
    author VARCHAR,
    comment TEXT,
    time_spent_seconds INTEGER,
    started_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Design

### REST API Endpoints

#### Authentication & Health
- `GET /api/health` - Health check
- `POST /api/connect` - Connect to Jira

#### Sprint Management
- `GET /api/sprints` - Get active sprints
- `GET /api/sprint/{sprint_id}` - Get sprint details
- `GET /api/sprint/{sprint_id}/report` - Get comprehensive sprint report

#### User Operations
- `GET /api/user/{username}/worklogs` - Get user work logs
- `GET /api/user/{username}/issues` - Get user assigned issues

#### Team Management
- `GET /api/capacity` - Get team capacity information

#### Alerts & Notifications
- `GET /api/alerts` - Get user alerts

#### Reporting
- `GET /api/reports/monthly` - Generate monthly reports

### Request/Response Patterns

#### Sprint Report Response
```json
{
  "sprint_id": 123,
  "summary": {
    "total_issues": 15,
    "total_points": 45,
    "completed_points": 30,
    "completion_percentage": 66.7
  },
  "status_distribution": {
    "Done": 8,
    "In Progress": 5,
    "To Do": 2
  },
  "burndown": {
    "total_points": 45,
    "completed_points": 30,
    "remaining_points": 15
  }
}
```

#### Work Log Response
```json
{
  "username": "john.doe",
  "period_days": 7,
  "total_worklogs": 12,
  "total_hours": 40.5,
  "worklogs": [
    {
      "id": 12345,
      "issue_key": "PROJ-123",
      "comment": "Implemented feature",
      "time_spent_seconds": 14400,
      "started": "2024-01-15T09:00:00Z"
    }
  ]
}
```

## Security Implementation

### Authentication
- **Jira API Token**: Secure token-based authentication
- **Environment Variables**: Sensitive data stored in `.env` files
- **CORS Configuration**: Cross-origin request handling

### Data Protection
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Error Handling**: Comprehensive exception handling without exposing internals

### Configuration Security
- **Secret Management**: Environment-based configuration
- **Token Expiration**: Configurable JWT token lifetimes
- **HTTPS Support**: Secure communication protocols

## Deployment Architecture

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   Streamlit     │    │   FastAPI       │
│   Port: 8501    │◄──►│   Port: 8000    │
└─────────────────┘    └─────────────────┘
```

### Production Considerations
- **Containerization**: Docker support for easy deployment
- **Load Balancing**: Multiple backend instances
- **Database**: PostgreSQL for production use
- **Caching**: Redis for session and data caching
- **Monitoring**: Health checks and logging

## Development Workflow

### Setup Process
1. **Environment Setup**: Python 3.8+ installation
2. **Dependencies**: Install requirements from `requirements.txt`
3. **Configuration**: Set up `.env` file with Jira credentials
4. **Database**: Automatic table creation on startup
5. **Running**: Separate processes for frontend and backend

### Development Commands
```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
streamlit run app.py --server.port 8501

# Quick Start
python quick_start.py
```

### Testing Strategy
- **API Testing**: FastAPI automatic OpenAPI documentation
- **Integration Testing**: Jira API integration tests
- **Frontend Testing**: Streamlit component testing
- **End-to-End**: Manual testing of complete workflows

### Code Organization
- **Separation of Concerns**: Clear separation between frontend and backend
- **Service Layer**: Business logic in dedicated service classes
- **Configuration Management**: Centralized configuration handling
- **Error Handling**: Consistent error handling patterns

## Performance Considerations

### Backend Optimization
- **Database Indexing**: Proper indexes on frequently queried fields
- **Connection Pooling**: SQLAlchemy connection management
- **Caching**: Jira API response caching
- **Async Operations**: Non-blocking API calls

### Frontend Optimization
- **Lazy Loading**: Load data on demand
- **Caching**: Session state management
- **Responsive Design**: Mobile-friendly interface
- **Chart Optimization**: Efficient Plotly rendering

## Future Enhancements

### Planned Features
- **Real-time Updates**: WebSocket integration for live data
- **Advanced Analytics**: Machine learning insights
- **Mobile App**: Native mobile application
- **Multi-tenant Support**: Multiple Jira instance support
- **Advanced Reporting**: Custom report builder
- **Integration APIs**: Third-party tool integrations

### Scalability Improvements
- **Microservices**: Service decomposition
- **Message Queues**: Asynchronous processing
- **Distributed Caching**: Redis cluster
- **Database Sharding**: Horizontal scaling
- **CDN Integration**: Static asset delivery

This architecture provides a solid foundation for a scalable, maintainable Jira management dashboard with clear separation of concerns and modern development practices. 