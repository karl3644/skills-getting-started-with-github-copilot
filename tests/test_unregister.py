"""Tests for the POST /activities/{activity_name}/unregister endpoint."""
import pytest


class TestUnregister:
    """Test suite for unregister functionality."""

    def test_unregister_existing_participant_success(self, client, fresh_activities):
        """Test successfully unregistering an existing participant."""
        # michael@mergington.edu is already signed up for Chess Club
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]
        assert "michael@mergington.edu" not in fresh_activities["Chess Club"]["participants"]

    def test_unregister_removes_from_participants_list(self, client, fresh_activities):
        """Test that unregister removes the participant from the list."""
        initial_count = len(fresh_activities["Chess Club"]["participants"])
        
        response = client.post(
            "/activities/Chess Club/unregister?email=daniel@mergington.edu"
        )
        
        assert response.status_code == 200
        assert len(fresh_activities["Chess Club"]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_activity_returns_404(self, client, fresh_activities):
        """Test that unregistering from non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up_returns_400(self, client, fresh_activities):
        """Test that unregistering a non-participant returns 400."""
        response = client.post(
            "/activities/Chess Club/unregister?email=notamember@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_then_signup_again(self, client, fresh_activities):
        """Test that a participant can signup again after unregistering."""
        # Unregister
        response1 = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response2.status_code == 200
        assert "michael@mergington.edu" in fresh_activities["Chess Club"]["participants"]

    def test_unregister_response_message_format(self, client, fresh_activities):
        """Test that unregister response message has correct format."""
        response = client.post(
            "/activities/Gym Class/unregister?email=john@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "john@mergington.edu" in data["message"]
        assert "Gym Class" in data["message"]

    def test_unregister_from_different_activities(self, client, fresh_activities):
        """Test unregistering from different activities independently."""
        # First signup to multiple activities
        client.post("/activities/Chess Club/signup?email=grace@mergington.edu")
        client.post("/activities/Gym Class/signup?email=grace@mergington.edu")
        
        # Unregister from Chess Club only
        response = client.post(
            "/activities/Chess Club/unregister?email=grace@mergington.edu"
        )
        
        assert response.status_code == 200
        assert "grace@mergington.edu" not in fresh_activities["Chess Club"]["participants"]
        # Should still be signed up for Gym Class
        assert "grace@mergington.edu" in fresh_activities["Gym Class"]["participants"]

    def test_double_unregister_returns_400(self, client, fresh_activities):
        """Test that unregistering twice returns an error the second time."""
        # First unregister succeeds
        response1 = client.post(
            "/activities/Gym Class/unregister?email=olivia@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.post(
            "/activities/Gym Class/unregister?email=olivia@mergington.edu"
        )
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]
