"""Tests for the GET /activities endpoint."""
import pytest


class TestGetActivities:
    """Test suite for retrieving activities."""

    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_correct_structure(self, client, fresh_activities):
        """Test that activities have required fields."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_includes_participants(self, client, fresh_activities):
        """Test that activities include registered participants."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert isinstance(chess_club["participants"], list)
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_shows_correct_availability(self, client, fresh_activities):
        """Test that max_participants and participants count are correct."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2
        # Frontend calculates: spots_left = max_participants - len(participants)
        spots_left = chess_club["max_participants"] - len(chess_club["participants"])
        assert spots_left == 10
