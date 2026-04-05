"""
Integration tests for the FastAPI activities application
Tests the API endpoints using FastAPI's TestClient
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are returned
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_initial_participants(self, client, reset_activities):
        """Test that activities include pre-populated participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club was initialized with 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client, reset_activities):
        """Test that root path redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "student@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]

    def test_signup_invalid_activity(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Non Existent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_signup_prevented(self, client, reset_activities):
        """Test that duplicate signup is prevented"""
        # First signup
        response1 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_invalid_email_format(self, client, reset_activities):
        """Test that invalid email format is rejected"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "notanemail"}
        )
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    def test_signup_invalid_email_missing_at_symbol(self, client, reset_activities):
        """Test that email without @ is rejected"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "studentmergington.edu"}
        )
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    def test_signup_invalid_email_missing_domain(self, client, reset_activities):
        """Test that email without domain is rejected"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "student@"}
        )
        
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    def test_signup_at_capacity_rejected(self, client, reset_activities):
        """Test that signup is rejected when activity is at max capacity"""
        # Art Club has max_participants = 10 and starts empty
        # Fill it up completely
        for i in range(10):
            client.post(
                "/activities/Art Club/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Try to add one more - should fail
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": "extra@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]

    def test_signup_multiple_users_same_activity(self, client, reset_activities):
        """Test that multiple users can sign up for the same activity"""
        for i in range(3):
            response = client.post(
                "/activities/Soccer Club/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
            assert response.status_code == 200
        
        # Verify all 3 are registered
        response = client.get("/activities")
        participants = response.json()["Soccer Club"]["participants"]
        
        assert len(participants) == 3
        for i in range(3):
            assert f"student{i}@mergington.edu" in participants

    def test_signup_user_can_join_multiple_activities(self, client, reset_activities):
        """Test that a user can sign up for multiple different activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for 3 different activities
        for activity in ["Basketball Team", "Soccer Club", "Drama Club"]:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify user is in all 3 activities
        response = client.get("/activities")
        activities = response.json()
        
        assert email in activities["Basketball Team"]["participants"]
        assert email in activities["Soccer Club"]["participants"]
        assert email in activities["Drama Club"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity"""
        # First signup
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "student@mergington.edu"}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "student@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        
        # Unregister
        client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": email}
        )
        
        # Verify removed
        response = client.get("/activities")
        activities = response.json()
        
        assert email not in activities["Basketball Team"]["participants"]

    def test_unregister_frees_up_capacity(self, client, reset_activities):
        """Test that unregistering frees up a spot for new signups"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Fill up Art Club (max 10)
        for i in range(10):
            client.post(
                "/activities/Art Club/signup",
                params={"email": f"filler{i}@mergington.edu"}
            )
        
        # Verify 11th signup fails
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": email1}
        )
        assert response.status_code == 400
        
        # Unregister one participant
        client.delete(
            "/activities/Art Club/unregister",
            params={"email": "filler0@mergington.edu"}
        )
        
        # Now signup should succeed
        response = client.post(
            "/activities/Art Club/signup",
            params={"email": email1}
        )
        assert response.status_code == 200

    def test_unregister_invalid_activity(self, client, reset_activities):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Non Existent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregister of non-existent student returns 400"""
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_then_resignup(self, client, reset_activities):
        """Test that user can re-signup after unregistering"""
        email = "student@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        
        # Unregister
        client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": email}
        )
        
        # Re-signup
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        
        # Verify back in activity
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball Team"]["participants"]


class TestSignupUnregisterFlow:
    """Tests for complete signup/unregister workflows"""

    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test a complex workflow with multiple signups and unregisters"""
        # Multiple users signup
        users = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        for user in users:
            response = client.post(
                "/activities/Debate Club/signup",
                params={"email": user}
            )
            assert response.status_code == 200
        
        # Verify all are registered
        response = client.get("/activities")
        assert len(response.json()["Debate Club"]["participants"]) == 3
        
        # Unregister one user
        client.delete(
            "/activities/Debate Club/unregister",
            params={"email": "user1@mergington.edu"}
        )
        
        # Verify 2 are left
        response = client.get("/activities")
        assert len(response.json()["Debate Club"]["participants"]) == 2
        assert "user1@mergington.edu" not in response.json()["Debate Club"]["participants"]
