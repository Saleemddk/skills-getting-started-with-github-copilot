"""
Integration tests for the /activities/{activity_name}/signup endpoint using AAA (Arrange-Act-Assert) pattern.
Tests focus on validating the signup logic, duplicate prevention, and capacity limits.
"""

import pytest


def test_successful_signup_adds_participant(client, reset_activities):
    """
    Test that a new participant can successfully sign up for an activity.
    
    AAA Pattern:
    - Arrange: Select an activity and an email that's not already signed up
    - Act: POST a signup request
    - Assert: Verify 200 response and participant is added
    """
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity_name]["participants"].copy()
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify participant was added
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    assert len(updated_participants) == len(initial_participants) + 1
    assert email in updated_participants


def test_duplicate_signup_rejected(client, reset_activities):
    """
    Test that a student cannot sign up for the same activity twice.
    This validates the bug fix that prevents duplicate registrations.
    
    AAA Pattern:
    - Arrange: Get an email already registered for an activity
    - Act: Try to POST signup with that email again
    - Assert: Verify 400 error and participant count unchanged
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    
    # Verify participant count didn't change
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity_name]["participants"])
    assert updated_count == initial_count


def test_signup_to_nonexistent_activity_returns_404(client, reset_activities):
    """
    Test that signing up for a non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Use an activity name that doesn't exist
    - Act: POST signup request to invalid activity
    - Assert: Verify 404 error and detail message
    """
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_to_full_activity_rejected(client, reset_activities):
    """
    Test that a student cannot sign up for an activity that is at full capacity.
    
    AAA Pattern:
    - Arrange: Create an activity with limited spots and fill it up
    - Act: Try to POST signup when at max capacity
    - Assert: Verify 400 error and capacity not exceeded
    """
    # Arrange
    activity_name = "Tennis Club"
    
    # Get current status
    initial_response = client.get("/activities")
    activity_data = initial_response.json()[activity_name]
    max_participants = activity_data["max_participants"]
    current_participants = len(activity_data["participants"])
    spots_available = max_participants - current_participants
    
    # Fill remaining spots with test emails
    for i in range(spots_available):
        email = f"fillup{i}@mergington.edu"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
    
    # Act - Try to signup when full
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "overfull@mergington.edu"}
    )
    
    # Assert
    assert response.status_code == 400
    assert "full" in response.json()["detail"]
    
    # Verify capacity is still at max
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity_name]["participants"])
    assert final_count == max_participants


def test_signup_empty_email_invalid(client, reset_activities):
    """
    Test that signing up with an empty email is handled properly.
    
    AAA Pattern:
    - Arrange: Activity exists, prepare empty email parameter
    - Act: POST signup with empty email
    - Assert: Verify request is rejected
    """
    # Arrange
    activity_name = "Chess Club"
    email = ""
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    # Should either return 400 or validate email format
    assert response.status_code in [400, 422]


def test_multiple_different_signups_successful(client, reset_activities):
    """
    Test that the same student can sign up for multiple different activities.
    
    AAA Pattern:
    - Arrange: Select same student and multiple different activities
    - Act: POST signup requests for each activity
    - Assert: Verify all signups succeed with 200 status
    """
    # Arrange
    email = "multiactivity@mergington.edu"
    activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
    
    # Act
    responses = []
    for activity_name in activities_to_join:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        responses.append(response)
    
    # Assert
    for response in responses:
        assert response.status_code == 200
    
    # Verify student is in all activities
    final_response = client.get("/activities")
    activities_data = final_response.json()
    for activity_name in activities_to_join:
        assert email in activities_data[activity_name]["participants"]
