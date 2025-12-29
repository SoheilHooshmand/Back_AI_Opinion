import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from project.models import Project, SiliconePerson, Question, Response as ResponseModel
from user.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="strongpassword123"
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def project(user):
    return Project.objects.create(
        user=user,
        title="Test Project",
        description="A test project"
    )


@pytest.fixture
def silicone_person(project):
    return SiliconePerson.objects.create(
        project=project,
        name="Alice",
        gender="Female",
        age=25,
        skin_color="Light"
    )


@pytest.fixture
def question(project):
    return Question.objects.create(
        project=project,
        body="What is AI?",
        real_answer="Artificial Intelligence"
    )



@pytest.mark.django_db
class TestProjectView:
    def test_get_projects(self, auth_client, project):
        url = reverse("project")
        response = auth_client.get(url)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert response.data[0]["title"] == "Test Project"

    def test_create_project(self, auth_client):
        url = reverse("project")
        data = {"title": "New Project", "description": "Demo description"}
        response = auth_client.post(url, data)
        assert response.status_code == 201
        assert Project.objects.filter(title="New Project").exists()

    def test_unauthenticated_project_access(self, api_client):
        url = reverse("project")
        response = api_client.get(url)
        assert response.status_code == 401



@pytest.mark.django_db
class TestSiliconPersonView:
    def test_get_silicone_persons(self, auth_client, project, silicone_person):
        url = reverse("silicon_person")
        response = auth_client.get(url, {"project_id": project.id})
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Alice"

    def test_create_silicone_persons(self, auth_client, project):
        url = reverse("silicon_person")
        payload = {
            "project_id": project.id,
            "siliconpersons": [
                {"name": "Bob", "gender": "Male", "age": 30, "skin_color": "Medium"},
                {"name": "Carol", "gender": "Female", "age": 27, "skin_color": "Dark"},
            ]
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == 201
        assert SiliconePerson.objects.filter(name="Bob").exists()
        assert SiliconePerson.objects.count() == 2 + 0



@pytest.mark.django_db
class TestSamplingViews:
    def test_get_question(self, auth_client, question):
        url = reverse("question")
        response = auth_client.get(url, {"question_id": question.id})
        assert response.status_code == 200
        assert "body" in response.data
        assert response.data["body"] == "What is AI?"

    def test_post_question(self, auth_client, project):
        url = reverse("question")
        payload = {"project_id": project.id, "body": "What is ML?", "real_answer": "Machine Learning"}
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == 201
        assert Question.objects.filter(body="What is ML?").exists()



@pytest.mark.django_db
class TestModelResponseView:
    def test_get_model_responses_completed(self, auth_client, project, question, silicone_person):
        # create mock model response
        ResponseModel.objects.create(
            question=question,
            silicone_person=silicone_person,
            raw_response="AI means Artificial Intelligence",
            gpt_model="gpt-5"
        )
        project.status = "completed"
        project.save()

        url = reverse("model_response")
        response = auth_client.get(url, {"project_id": project.id, "question_id": question.id})
        assert response.status_code == 200
        assert "data" in response.data
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["response_of_model"].startswith("AI")

    def test_get_model_responses_not_completed(self, auth_client, project, question):
        url = reverse("model_response")
        response = auth_client.get(url, {"project_id": project.id, "question_id": question.id})
        assert response.status_code == 200
        assert response.data["message"] == "mission did not complete!"
