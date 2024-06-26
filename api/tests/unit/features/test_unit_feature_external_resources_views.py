import datetime

import pytest
import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from environments.models import Environment
from environments.permissions.constants import UPDATE_FEATURE_STATE
from features.feature_external_resources.models import FeatureExternalResource
from features.models import Feature, FeatureState
from features.serializers import FeatureStateSerializerBasic
from integrations.github.github import GithubData
from integrations.github.models import GithubConfiguration, GithubRepository
from projects.models import Project
from tests.types import WithEnvironmentPermissionsCallable
from webhooks.webhooks import WebhookEventType

_django_json_encoder_default = DjangoJSONEncoder().default


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def raise_for_status(self) -> None:
            pass

        def json(self):
            return self.json_data

    return MockResponse(json_data={"data": "data"}, status_code=200)


@freeze_time("2024-01-01")
def test_create_feature_external_resource(
    admin_client_new: APIClient,
    feature_with_value: Feature,
    project: Project,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
    mocker,
) -> None:
    # Given
    mock_generate_token = mocker.patch(
        "integrations.github.github.generate_token",
    )
    mock_generate_token.return_value = "mocked_token"
    github_request_mock = mocker.patch(
        "requests.post", side_effect=mocked_requests_post
    )
    datetime_now = datetime.datetime.now()

    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://github.com/repoowner/repo-name/issues/35",
        "feature": feature_with_value.id,
        "metadata": {"status": "open"},
    }

    url = reverse(
        "api-v1:projects:feature-external-resources-list",
        kwargs={"project_pk": project.id, "feature_pk": feature_with_value.id},
    )

    # When
    response = admin_client_new.post(
        url, data=feature_external_resource_data, format="json"
    )

    # Then
    github_request_mock.assert_called_with(
        "https://api.github.com/repos/repoowner/repo-name/issues/35/comments",
        json={
            "body": f"### This pull request is linked to a Flagsmith Feature (`feature_with_value`):\n**Test Environment**\n- [ ] Disabled\nunicode\n```value```\n\nLast Updated {datetime_now.strftime('%dth %b %Y %I:%M%p')}"  # noqa E501
        },
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "Bearer mocked_token",
        },
        timeout=10,
    )
    assert response.status_code == status.HTTP_201_CREATED
    # assert that the payload has been save to the database
    feature_external_resources = FeatureExternalResource.objects.filter(
        feature=feature_with_value,
        type=feature_external_resource_data["type"],
        url=feature_external_resource_data["url"],
    ).all()
    assert len(feature_external_resources) == 1
    assert feature_external_resources[0].metadata == json.dumps(
        feature_external_resource_data["metadata"], default=_django_json_encoder_default
    )
    assert feature_external_resources[0].feature == feature_with_value
    assert feature_external_resources[0].type == feature_external_resource_data["type"]
    assert feature_external_resources[0].url == feature_external_resource_data["url"]

    # And When
    url = reverse(
        "api-v1:projects:feature-external-resources-list",
        kwargs={"project_pk": project.id, "feature_pk": feature_with_value.id},
    )

    response = admin_client_new.get(url)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert (
        response.json()["results"][0]["type"] == feature_external_resource_data["type"]
    )
    assert response.json()["results"][0]["url"] == feature_external_resource_data["url"]
    assert (
        response.json()["results"][0]["metadata"]
        == feature_external_resource_data["metadata"]
    )


def test_cannot_create_feature_external_resource_when_doesnt_have_a_valid_github_integration(
    admin_client_new: APIClient,
    feature: Feature,
    project: Project,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://example.com?item=create",
        "feature": feature.id,
        "metadata": {"status": "open"},
    }
    url = reverse(
        "api-v1:projects:feature-external-resources-list", args=[project.id, feature.id]
    )

    # When
    response = admin_client_new.post(
        url, data=feature_external_resource_data, format="json"
    )

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cannot_create_feature_external_resource_when_doesnt_have_permissions(
    admin_client_new: APIClient,
    feature: Feature,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://example.com?item=create",
        "feature": feature.id,
        "metadata": {"status": "open"},
    }
    url = reverse(
        "api-v1:projects:feature-external-resources-list", args=[2, feature.id]
    )

    # When
    response = admin_client_new.post(
        url, data=feature_external_resource_data, format="json"
    )

    # Then
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_cannot_create_feature_external_resource_when_the_type_is_incorrect(
    admin_client_new: APIClient,
    feature: Feature,
    project: Project,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "UNKNOWN_TYPE",
        "url": "https://example.com",
        "feature": feature.id,
    }
    url = reverse(
        "api-v1:projects:feature-external-resources-list", args=[project.id, feature.id]
    )

    # When
    response = admin_client_new.post(url, data=feature_external_resource_data)
    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_cannot_create_feature_external_resource_due_to_unique_constraint(
    admin_client_new: APIClient,
    feature: Feature,
    feature_external_resource: FeatureExternalResource,
    project: Project,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://github.com/userexample/example-project-repo/issues/11",
        "feature": feature.id,
    }
    url = reverse(
        "api-v1:projects:feature-external-resources-list", args=[project.id, feature.id]
    )

    # When
    response = admin_client_new.post(url, data=feature_external_resource_data)

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Duplication error. The feature already has this resource URI"
        in response.json()[0]
    )


def test_delete_feature_external_resource(
    admin_client_new: APIClient,
    feature_external_resource: FeatureExternalResource,
    feature: Feature,
    project: Project,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
    mocker,
) -> None:
    # Given
    mock_generate_token = mocker.patch(
        "integrations.github.github.generate_token",
    )
    mock_generate_token.return_value = "mocked_token"
    github_request_mock = mocker.patch(
        "requests.post", side_effect=mocked_requests_post
    )
    url = reverse(
        "api-v1:projects:feature-external-resources-detail",
        args=[project.id, feature.id, feature_external_resource.id],
    )

    # When
    response = admin_client_new.delete(url)

    # Then
    github_request_mock.assert_called_with(
        "https://api.github.com/repos/userexample/example-project-repo/issues/11/comments",
        json={
            "body": "### The feature flag `Test Feature1` was unlinked from the issue/PR"
        },
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "Bearer mocked_token",
        },
        timeout=10,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not FeatureExternalResource.objects.filter(
        id=feature_external_resource.id
    ).exists()


def test_get_feature_external_resources(
    admin_client_new: APIClient,
    feature_external_resource: FeatureExternalResource,
    feature: Feature,
    project: Project,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
) -> None:
    # Given
    url = reverse(
        "api-v1:projects:feature-external-resources-list",
        kwargs={"project_pk": project.id, "feature_pk": feature.id},
    )

    # When
    response = admin_client_new.get(url)

    # Then
    assert response.status_code == status.HTTP_200_OK


def test_get_feature_external_resource(
    admin_client_new: APIClient,
    feature_external_resource: FeatureExternalResource,
    feature: Feature,
    project: Project,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
) -> None:
    # Given
    url = reverse(
        "api-v1:projects:feature-external-resources-detail",
        args=[project.id, feature.id, feature_external_resource.id],
    )

    # When
    response = admin_client_new.get(url)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == feature_external_resource.id
    assert response.data["type"] == feature_external_resource.type
    assert response.data["url"] == feature_external_resource.url


@pytest.mark.parametrize(
    "event_type",
    [
        ("update"),
        ("delete"),
    ],
)
def test_create_github_comment_on_feature_state_updated(  # noqa: C901
    staff_client: APIClient,
    with_environment_permissions: WithEnvironmentPermissionsCallable,
    feature_external_resource: FeatureExternalResource,
    feature: Feature,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
    mocker,
    environment: Environment,
    event_type: str,
) -> None:
    # Given
    with_environment_permissions([UPDATE_FEATURE_STATE])
    feature_state = FeatureState.objects.get(
        feature=feature, environment=environment.id
    )
    mock_generate_token = mocker.patch(
        "integrations.github.github.generate_token",
    )
    mock_generate_token.return_value = "mocked_token"
    github_request_mock = mocker.patch(
        "requests.post", side_effect=mocked_requests_post
    )

    feature_state_value = feature_state.get_feature_state_value()
    feature_env_data = {}
    feature_env_data["feature_state_value"] = feature_state_value
    feature_env_data["feature_state_value_type"] = (
        feature_state.get_feature_state_value_type(feature_state_value)
    )
    feature_env_data["environment_name"] = environment.name
    feature_env_data["feature_value"] = feature_state.enabled
    if event_type == "update":
        mock_generate_data = mocker.patch(
            "integrations.github.github.generate_data",
            return_value=GithubData(
                installation_id=github_configuration.installation_id,
                feature_id=feature.id,
                feature_name=feature.name,
                type=feature_external_resource.type,
                feature_states=[feature_env_data],
                url=feature_external_resource.url,
            ),
        )

        mocker.patch(
            "integrations.github.tasks.generate_body_comment",
            return_value="Flag updated",
        )

    payload = dict(FeatureStateSerializerBasic(instance=feature_state).data)

    payload["enabled"] = not feature_state.enabled
    url = reverse(
        viewname="api-v1:environments:environment-featurestates-detail",
        kwargs={"environment_api_key": environment.api_key, "pk": feature_state.id},
    )

    # When
    if event_type == "update":
        response = staff_client.put(path=url, data=payload, format="json")
    elif event_type == "delete":
        response = staff_client.delete(path=url)

    # Then
    if event_type == "update":
        assert response.status_code == status.HTTP_200_OK
    elif event_type == "delete":
        assert response.status_code == status.HTTP_204_NO_CONTENT

    if event_type == "update":
        github_request_mock.assert_called_with(
            "https://api.github.com/repos/userexample/example-project-repo/issues/11/comments",
            json={"body": "Flag updated"},
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "Bearer mocked_token",
            },
            timeout=10,
        )
    elif event_type == "delete":
        github_request_mock.assert_called_with(
            "https://api.github.com/repos/userexample/example-project-repo/issues/11/comments",
            json={"body": "### The Feature Flag `Test Feature1` was deleted"},
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": "Bearer mocked_token",
            },
            timeout=10,
        )
    if event_type == "update":
        mock_generate_data.assert_called_with(
            github_configuration=github_configuration,
            feature_id=feature.id,
            feature_name=feature.name,
            type=WebhookEventType.FLAG_UPDATED.value,
            feature_states=[feature_state],
        )
