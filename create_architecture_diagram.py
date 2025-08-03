import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Set up the figure with better proportions
fig, ax = plt.subplots(1, 1, figsize=(20, 16))
ax.set_xlim(0, 20)
ax.set_ylim(0, 16)
ax.axis('off')

# Clean, modern color palette
colors = {
    'frontend': '#4CAF50',      # Green
    'backend': '#2196F3',       # Blue
    'database': '#FF9800',      # Orange
    'external': '#9C27B0',      # Purple
    'service': '#607D8B',       # Blue Grey
    'background': '#F5F5F5'     # Light Grey
}

# Set background color
ax.set_facecolor(colors['background'])

# Title
ax.text(10, 15.5, 'Jira Management Dashboard', 
        fontsize=28, fontweight='bold', ha='center', color='#2C3E50')
ax.text(10, 15, 'Architecture Overview', 
        fontsize=18, ha='center', color='#7F8C8D', style='italic')

# Main layers with proper spacing
# Frontend Layer
frontend_box = FancyBboxPatch((1, 12), 18, 2.5, 
                             boxstyle="round,pad=0.2", 
                             facecolor=colors['frontend'], 
                             edgecolor='white', linewidth=2)
ax.add_patch(frontend_box)
ax.text(10, 13.5, 'Frontend Layer', fontsize=22, fontweight='bold', ha='center', color='white')
ax.text(10, 12.8, 'Streamlit Web Application', fontsize=16, ha='center', color='white', alpha=0.9)

# Frontend features in columns
frontend_features = [
    "• Manager Dashboard",
    "• Developer Dashboard", 
    "• Sprint Reports",
    "• Capacity Planning",
    "• Work Logs",
    "• Real-time Charts"
]

for i, feature in enumerate(frontend_features):
    x_pos = 2.5 + (i % 3) * 5.5
    y_pos = 12.3 - (i // 3) * 0.4
    ax.text(x_pos, y_pos, feature, fontsize=12, ha='left', color='white', fontweight='medium')

# Backend Layer
backend_box = FancyBboxPatch((1, 8.5), 18, 2.5, 
                            boxstyle="round,pad=0.2", 
                            facecolor=colors['backend'], 
                            edgecolor='white', linewidth=2)
ax.add_patch(backend_box)
ax.text(10, 10, 'Backend Layer', fontsize=22, fontweight='bold', ha='center', color='white')
ax.text(10, 9.3, 'FastAPI REST API', fontsize=16, ha='center', color='white', alpha=0.9)

# Backend features in columns
backend_features = [
    "• REST API Endpoints",
    "• Jira Integration",
    "• AI Task Organization",
    "• Report Generation",
    "• Capacity Planning",
    "• Authentication"
]

for i, feature in enumerate(backend_features):
    x_pos = 2.5 + (i % 3) * 5.5
    y_pos = 8.8 - (i // 3) * 0.4
    ax.text(x_pos, y_pos, feature, fontsize=12, ha='left', color='white', fontweight='medium')

# Data Layer (Database + External Services)
# Database
db_box = FancyBboxPatch((1, 5), 8.5, 2.5, 
                       boxstyle="round,pad=0.2", 
                       facecolor=colors['database'], 
                       edgecolor='white', linewidth=2)
ax.add_patch(db_box)
ax.text(5.25, 6.5, 'Database Layer', fontsize=20, fontweight='bold', ha='center', color='white')
ax.text(5.25, 5.8, 'SQLite Database', fontsize=14, ha='center', color='white', alpha=0.9)

db_features = ["• Sprints", "• Issues", "• Work Logs", "• Users", "• Alerts"]
for i, feature in enumerate(db_features):
    x_pos = 2 + (i % 2) * 3
    y_pos = 5.3 - (i // 2) * 0.4
    ax.text(x_pos, y_pos, feature, fontsize=11, ha='left', color='white', fontweight='medium')

# External Services
external_box = FancyBboxPatch((10.5, 5), 8.5, 2.5, 
                             boxstyle="round,pad=0.2", 
                             facecolor=colors['external'], 
                             edgecolor='white', linewidth=2)
ax.add_patch(external_box)
ax.text(14.75, 6.5, 'External Services', fontsize=20, fontweight='bold', ha='center', color='white')
ax.text(14.75, 5.8, 'Third-party APIs', fontsize=14, ha='center', color='white', alpha=0.9)

external_features = ["• Jira API", "• OpenAI API", "• Outlook Calendar", "• Email Service"]
for i, feature in enumerate(external_features):
    x_pos = 11.5 + (i % 2) * 3
    y_pos = 5.3 - (i // 2) * 0.4
    ax.text(x_pos, y_pos, feature, fontsize=11, ha='left', color='white', fontweight='medium')

# Service Components Layer
service_box = FancyBboxPatch((1, 1.5), 18, 2.5, 
                            boxstyle="round,pad=0.2", 
                            facecolor=colors['service'], 
                            edgecolor='white', linewidth=2)
ax.add_patch(service_box)
ax.text(10, 3, 'Service Components', fontsize=20, fontweight='bold', ha='center', color='white')
ax.text(10, 2.3, 'Core Business Logic Services', fontsize=14, ha='center', color='white', alpha=0.9)

# Service components in a grid
services = [
    ("Jira Service", "Issue Management\nSprint Data\nWork Logs"),
    ("AI Service", "Task Organization\nPriority Analysis\nSchedule Optimization"),
    ("Report Service", "Sprint Reports\nCapacity Reports\nMonthly Reports"),
    ("Outlook Service", "Calendar Integration\nMeeting Scheduling\nAvailability Check")
]

for i, (name, features) in enumerate(services):
    x_pos = 2.5 + (i % 4) * 4
    y_pos = 1.8
    ax.text(x_pos, y_pos, name, fontsize=12, fontweight='bold', ha='center', color='white')
    ax.text(x_pos, y_pos - 0.3, features, fontsize=9, ha='center', color='white', alpha=0.9)

# Connection arrows with labels
# Frontend to Backend
arrow1 = ConnectionPatch((10, 12), (10, 11), "data", "data",
                        arrowstyle="->", shrinkA=10, shrinkB=10,
                        mutation_scale=30, fc="#34495E", linewidth=3)
ax.add_patch(arrow1)
ax.text(11, 11.5, 'HTTP/REST API', fontsize=14, ha='left', fontweight='bold', color='#2C3E50',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='#BDC3C7'))

# Backend to Database
arrow2 = ConnectionPatch((5.25, 8.5), (5.25, 7.5), "data", "data",
                        arrowstyle="->", shrinkA=10, shrinkB=10,
                        mutation_scale=30, fc="#34495E", linewidth=3)
ax.add_patch(arrow2)
ax.text(6.5, 8, 'SQLAlchemy ORM', fontsize=14, ha='left', fontweight='bold', color='#2C3E50',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='#BDC3C7'))

# Backend to External Services
arrow3 = ConnectionPatch((14.75, 8.5), (14.75, 7.5), "data", "data",
                        arrowstyle="->", shrinkA=10, shrinkB=10,
                        mutation_scale=30, fc="#34495E", linewidth=3)
ax.add_patch(arrow3)
ax.text(16, 8, 'API Calls', fontsize=14, ha='left', fontweight='bold', color='#2C3E50',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='#BDC3C7'))

# Backend to Services
arrow4 = ConnectionPatch((10, 8.5), (10, 4), "data", "data",
                        arrowstyle="->", shrinkA=10, shrinkB=10,
                        mutation_scale=30, fc="#34495E", linewidth=3)
ax.add_patch(arrow4)
ax.text(11, 6.5, 'Service Calls', fontsize=14, ha='left', fontweight='bold', color='#2C3E50',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='#BDC3C7'))

# Technology Stack Box
tech_box = FancyBboxPatch((0.5, 0.2), 19, 0.8, 
                         boxstyle="round,pad=0.1", 
                         facecolor='white', 
                         edgecolor='#BDC3C7', linewidth=1)
ax.add_patch(tech_box)
ax.text(10, 0.7, 'Technology Stack', fontsize=16, fontweight='bold', ha='center', color='#2C3E50')

tech_stack = [
    "Frontend: Streamlit, Plotly, Pandas",
    "Backend: FastAPI, SQLAlchemy, Pydantic", 
    "Database: SQLite",
    "External: Jira API, OpenAI API, Outlook API"
]

for i, tech in enumerate(tech_stack):
    x_pos = 1 + (i % 2) * 9.5
    y_pos = 0.4
    ax.text(x_pos, y_pos, tech, fontsize=11, ha='left', color='#34495E', fontweight='medium')

# Add subtle grid lines for better visual organization
for i in range(1, 20):
    ax.axvline(x=i, color='#E8E8E8', alpha=0.3, linewidth=0.5)
for i in range(1, 16):
    ax.axhline(y=i, color='#E8E8E8', alpha=0.3, linewidth=0.5)

plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight', facecolor=colors['background'])
plt.close()

print("Clean and beautiful architecture diagram saved as 'architecture_diagram.png'") 