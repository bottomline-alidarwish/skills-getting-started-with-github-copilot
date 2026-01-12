"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    
    # Store original state
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
        "Basketball": {
            "description": "Team sport and basketball skills development",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation skills and compete in debates",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["alex@mergington.edu"]
        },
        "Math Club": {
            "description": "Solve challenging math problems and compete in competitions",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "zoe@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities_data = response.json()
        
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert len(activities_data) == 9

    def test_get_activities_returns_activity_details(self, reset_activities):
        """Test that activities have required fields"""
        response = client.get("/activities")
        activities_data = response.json()
        
        chess_club = activities_data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_includes_participants(self, reset_activities):
        """Test that activities include participant list"""
        response = client.get("/activities")
        activities_data = response.json()
        
        chess_club = activities_data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self, reset_activities):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_duplicate_participant_fails(self, reset_activities):
        """Test that signing up the same participant twice fails"""
        # First signup succeeds
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_updates_participant_count(self, reset_activities):
        """Test that signup updates the participant count"""
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Basketball"]["participants"])
        
        client.post(
            "/activities/Basketball/signup",
            params={"email": "newcomer@mergington.edu"}
        )
        
        response2 = client.get("/activities")
        updated_count = len(response2.json()["Basketball"]["participants"])
        
        assert updated_count == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self, reset_activities):
        """Test unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_nonexistent_participant_fails(self, reset_activities):
        """Test that unregistering a non-signed-up participant fails"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_updates_participant_list(self, reset_activities):
        """Test that unregister removes participant from list"""
        response1 = client.get("/activities")
        assert "michael@mergington.edu" in response1.json()["Chess Club"]["participants"]
        
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response2 = client.get("/activities")
        assert "michael@mergington.edu" not in response2.json()["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
