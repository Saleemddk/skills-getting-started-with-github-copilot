"""
Integration tests for the /activities endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


def test_get_activities_returns_all_activities(client, reset_activities):
    """
    Test that GET /activities returns all available activities.
    
    AAA Pattern:
    - Arrange: Client is ready (provided by fixture)
    - Act: Make GET request to /activities
    - Assert: Verify response contains all activities
    """
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Class",
        "Drama Club",
        "Debate Team",
        "Math Club"
    ]
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert response.status_code == 200
    assert len(activities) == len(expected_activities)
    for activity_name in expected_activities:
        assert activity_name in activities


def test_activities_have_required_fields(client, reset_activities):
    """
    Test that each activity has the required fields.
    
    AAA Pattern:
    - Arrange: Client is ready (provided by fixture)
    - Act: Make GET request to /activities
    - Assert: Verify each activity has description, schedule, max_participants, participants
    """
    # Arrange
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert response.status_code == 200
    for activity_name, activity_data in activities.items():
        for field in required_fields:
            assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"


def test_activities_have_participants_list(client, reset_activities):
    """
    Test that each activity has a participants list populated.
    
    AAA Pattern:
    - Arrange: Client is ready (provided by fixture)
    - Act: Make GET request to /activities
    - Assert: Verify each activity has participants list with members
    """
    # Arrange
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert response.status_code == 200
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list), \
            f"Activity '{activity_name}' participants is not a list"
        assert len(activity_data["participants"]) > 0, \
            f"Activity '{activity_name}' has no participants"


def test_activities_have_valid_capacity(client, reset_activities):
    """
    Test that participants count does not exceed max_participants.
    
    AAA Pattern:
    - Arrange: Client is ready (provided by fixture)
    - Act: Make GET request to /activities
    - Assert: Verify participants count <= max_participants for each activity
    """
    # Arrange
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert response.status_code == 200
    for activity_name, activity_data in activities.items():
        participants_count = len(activity_data["participants"])
        max_participants = activity_data["max_participants"]
        assert participants_count <= max_participants, \
            f"Activity '{activity_name}' has {participants_count} participants but max is {max_participants}"
