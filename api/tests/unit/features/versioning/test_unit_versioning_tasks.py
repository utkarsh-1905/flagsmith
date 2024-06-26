from pytest_mock import MockerFixture

from environments.identities.models import Identity
from environments.models import Environment
from features.models import Feature, FeatureSegment, FeatureState
from features.versioning.models import EnvironmentFeatureVersion
from features.versioning.tasks import (
    disable_v2_versioning,
    enable_v2_versioning,
    trigger_update_version_webhooks,
)
from features.versioning.versioning_service import (
    get_environment_flags_queryset,
)
from segments.models import Segment
from users.models import FFAdminUser
from webhooks.webhooks import WebhookEventType


def test_enable_v2_versioning(
    environment: Environment, feature: Feature, multivariate_feature: Feature
) -> None:
    # When
    enable_v2_versioning(environment.id)

    # Then
    assert EnvironmentFeatureVersion.objects.filter(
        environment=environment, feature=feature
    ).exists()
    assert EnvironmentFeatureVersion.objects.filter(
        environment=environment, feature=multivariate_feature
    ).exists()

    environment.refresh_from_db()
    assert environment.use_v2_feature_versioning is True


def test_disable_v2_versioning(
    environment_v2_versioning: Environment,
    feature: Feature,
    segment: Segment,
    staff_user: FFAdminUser,
    identity: Identity,
) -> None:
    # Given
    # First, let's create a new version for the given feature which we'll also add a segment override to
    v2 = EnvironmentFeatureVersion.objects.create(
        environment=environment_v2_versioning, feature=feature
    )

    v2_environment_flag = v2.feature_states.filter(feature=feature).first()
    v2_environment_flag.enabled = True
    v2_environment_flag.save()

    FeatureState.objects.create(
        feature_segment=FeatureSegment.objects.create(
            environment=environment_v2_versioning,
            feature=feature,
            segment=segment,
            environment_feature_version=v2,
        ),
        feature=feature,
        environment=environment_v2_versioning,
        enabled=True,
        environment_feature_version=v2,
    )

    v2.publish(staff_user)

    # Now, let's create a new version which we won't publish (and hence should be ignored after we disabled
    # v2 versioning)
    v3 = EnvironmentFeatureVersion.objects.create(
        environment=environment_v2_versioning, feature=feature
    )

    v3_environment_flag = v3.feature_states.filter(feature=feature).first()
    v3_environment_flag.enabled = False
    v3_environment_flag.save()

    # Let's also create an identity override to confirm it is not affected.
    FeatureState.objects.create(
        identity=identity,
        feature=feature,
        enabled=True,
        environment=environment_v2_versioning,
    )

    # When
    disable_v2_versioning(environment_v2_versioning.id)
    environment_v2_versioning.refresh_from_db()

    # Then
    latest_feature_states = get_environment_flags_queryset(
        environment=environment_v2_versioning
    )

    assert latest_feature_states.count() == 3
    assert (
        latest_feature_states.filter(
            feature=feature, feature_segment__isnull=True, identity__isnull=True
        )
        .first()
        .enabled
        is True
    )
    assert (
        latest_feature_states.filter(feature=feature, feature_segment__segment=segment)
        .first()
        .enabled
        is True
    )
    assert (
        latest_feature_states.filter(feature=feature, identity=identity).first().enabled
        is True
    )


def test_trigger_update_version_webhooks(
    environment_v2_versioning: Environment, feature: Feature, mocker: MockerFixture
) -> None:
    # Given
    version = EnvironmentFeatureVersion.objects.get(
        feature=feature, environment=environment_v2_versioning
    )
    feature_state = version.feature_states.first()

    mock_call_environment_webhooks = mocker.patch(
        "features.versioning.tasks.call_environment_webhooks"
    )

    # When
    trigger_update_version_webhooks(str(version.uuid))

    # Then
    mock_call_environment_webhooks.assert_called_once_with(
        environment=environment_v2_versioning,
        data={
            "uuid": str(version.uuid),
            "feature": {"id": feature.id, "name": feature.name},
            "published_by": None,
            "feature_states": [
                {
                    "enabled": feature_state.enabled,
                    "value": feature_state.get_feature_state_value(),
                }
            ],
        },
        event_type=WebhookEventType.NEW_VERSION_PUBLISHED,
    )
