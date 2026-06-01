"""Tests for the POST /activities/{activity_name}/signup endpoint."""
import pytest


class TestSignup:
    """Test suite for signup functionality."""

    def test_signup_new_participant_success(self, client, fresh_activities):
        """Test successfully signing up a new participant to an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in fresh_activities["Chess Club"]["participants"]

    def test_signup_updates_participant_list(self, client, fresh_activities):
        """Test that signup updates the participants list correctly."""
        initial_count = len(fresh_activities["Chess Club"]["participants"])
        
        response = client.post(
            "/activities/Chess Club/signup?email=alice@mergington.edu"
        )
        
        assert response.status_code == 200
        assert len(fresh_activities["Chess Club"]["participants"]) == initial_count + 1

    def test_signup_to_different_activities(self, client, fresh_activities):
        """Test signing up to multiple activities."""
        client.post("/activities/Chess Club/signup?email=bob@mergington.edu")
        response = client.post("/activities/Gym Class/signup?email=bob@mergington.edu")
        
        assert response.status_code == 200
        assert "bob@mergington.edu" in fresh_activities["Chess Club"]["participants"]
        assert "bob@mergington.edu" in fresh_activities["Gym Class"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities):
        """Test that signing up to a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant_returns_400(self, client, fresh_activities):
        """Test that duplicate signup is rejected (the bug fix)."""
        # michael@mergington.edu is already signed up for Chess Club
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_duplicate_rejected_across_requests(self, client, fresh_activities):
        """Test duplicate prevention across multiple requests."""
        # First signup succeeds
        response1 = client.post(
            "/activities/Gym Class/signup?email=charlie@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup for same student/activity fails
        response2 = client.post(
            "/activities/Gym Class/signup?email=charlie@mergington.edu"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_response_message_format(self, client, fresh_activities):
        """Test that signup response message has correct format."""
        response = client.post(
            "/activities/Programming Class/signup?email=diana@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "diana@mergington.edu" in data["message"]
        assert "Programming Class" in data["message"]

    def test_signup_with_different_email_to_same_activity(self, client, fresh_activities):
        """Test that different students can sign up for the same activity."""
        response1 = client.post(
            "/activities/Chess Club/signup?email=eve@mergington.edu"
        )
        response2 = client.post(
            "/activities/Chess Club/signup?email=frank@mergington.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert "eve@mergington.edu" in fresh_activities["Chess Club"]["participants"]
        assert "frank@mergington.edu" in fresh_activities["Chess Club"]["participants"]
