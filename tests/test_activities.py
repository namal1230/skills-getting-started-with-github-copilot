"""
Integration tests for the activities API using AAA (Arrange-Act-Assert) pattern
"""


class TestGetActivities:
    def test_get_all_activities(self, client):
        """Test retrieving all available activities"""
        # Arrange: No setup needed, activities are pre-populated by fixture

        # Act: Make GET request to activities endpoint
        response = client.get("/activities")

        # Assert: Verify response status and content
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 2
        assert len(data["Chess Club"]["participants"]) == 1


class TestSignupForActivity:
    def test_signup_new_participant_successfully(self, client):
        """Test successfully signing up a new participant"""
        # Arrange: Prepare email for a new participant
        email = "emma@mergington.edu"
        activity_name = "Programming Class"

        # Act: Sign up the participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify successful signup
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Assert: Verify participant was added to activity
        activities_response = client.get("/activities").json()
        assert email in activities_response[activity_name]["participants"]

    def test_signup_duplicate_participant_rejected(self, client):
        """Test that duplicate signups are rejected"""
        # Arrange: Use an existing participant
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act: Attempt to sign up already registered participant
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify request fails with 400
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_to_nonexistent_activity_fails(self, client):
        """Test that signup to non-existent activity fails"""
        # Arrange: Use a non-existent activity name
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act: Attempt to sign up for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify request fails with 404
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    def test_unregister_participant_successfully(self, client):
        """Test successfully unregistering a participant"""
        # Arrange: Use existing participant in Chess Club
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act: Unregister the participant
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: Verify successful unregister
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Assert: Verify participant was removed
        activities_response = client.get("/activities").json()
        assert email not in activities_response[activity_name]["participants"]

    def test_unregister_nonregistered_participant_fails(self, client):
        """Test that unregistering non-registered participant fails"""
        # Arrange: Use a participant not registered for Programming Class
        email = "nonexistent@mergington.edu"
        activity_name = "Programming Class"

        # Act: Attempt to unregister non-registered participant
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: Verify request fails with 400
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregister from non-existent activity fails"""
        # Arrange: Use non-existent activity
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act: Attempt to unregister from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: Verify request fails with 404
        assert response.status_code == 404


class TestRootEndpoint:
    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to static index.html"""
        # Arrange: No setup needed

        # Act: Make GET request to root without following redirects
        response = client.get("/", follow_redirects=False)

        # Assert: Verify 307 redirect to index.html
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
