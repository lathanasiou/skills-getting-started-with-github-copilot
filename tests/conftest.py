"""
Pytest configuration and fixtures for the FastAPI application tests
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 4:30 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art forms and create masterpieces",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Debate Club": {
            "description": "Engage in debates and develop argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about science",
            "schedule": "Tuesdays, 3:00 PM - 4:00 PM",
            "max_participants": 16,
            "participants": []
        }
    }
    
    # Clear current activities and repopulate with originals
    activities.clear()
    activities.update(original_activities)
    
    yield activities
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)
