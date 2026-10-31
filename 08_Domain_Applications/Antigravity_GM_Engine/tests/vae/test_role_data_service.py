"""
Tests for VAE Pillar 3: Role-Specific Data Service and Negative Access Control.
Verifies:
- Segregated data queries for GM, Coach, and Player.
- Strict negative ACL (unauthorized role queries are rejected).
- Deterministic analysis for permitted views (e.g. GM cap space, Coach rotation, Player growth).
"""

import pytest
from src.vae.contracts import RoleType, RoleDataQuery
from src.vae.role_data_service import VAERoleDataService


@pytest.fixture
def data_service():
    return VAERoleDataService()


def test_gm_permitted_query(data_service):
    """Verifies that GM can access finance projection."""
    query = RoleDataQuery(
        query_id="q-gm-01",
        requester_role=RoleType.GM,
        target_category="finance_projection",
        save_id="SAVE_01",
        season="2021-22",
    )
    view = data_service.query_role_view(query)
    assert view.access_granted is True
    assert view.rejection_reason is None
    assert "salary_cap" in view.data
    assert view.data["salary_cap"] == 112_414_000


def test_coach_permitted_query(data_service):
    """Verifies that Coach can access rotation data."""
    query = RoleDataQuery(
        query_id="q-coach-01",
        requester_role=RoleType.COACH,
        target_category="rotation",
        save_id="SAVE_01",
        season="2021-22",
    )
    view = data_service.query_role_view(query)
    assert view.access_granted is True
    assert view.data["total_target_minutes"] == 240


def test_player_permitted_query(data_service):
    """Verifies that Player can access own attribute and growth data."""
    query = RoleDataQuery(
        query_id="q-player-01",
        requester_role=RoleType.PLAYER,
        target_category="own_attribute_and_growth",
        save_id="SAVE_01",
        season="2021-22",
        object_id="PL_23",
    )
    view = data_service.query_role_view(query)
    assert view.access_granted is True
    assert view.data["overall_rating"] == 84
    assert view.data["potential"] == 89


def test_negative_acl_rejection(data_service):
    """Verifies that cross-role access is denied by negative ACL."""
    # 1. Player trying to read GM finance projection
    query_player_to_gm = RoleDataQuery(
        query_id="q-leak-01",
        requester_role=RoleType.PLAYER,
        target_category="finance_projection",
        save_id="SAVE_01",
        season="2021-22",
    )
    view1 = data_service.query_role_view(query_player_to_gm)
    assert view1.access_granted is False
    assert "ACCESS_DENIED" in view1.rejection_reason

    # 2. Coach trying to read GM finance projection
    query_coach_to_gm = RoleDataQuery(
        query_id="q-leak-02",
        requester_role=RoleType.COACH,
        target_category="finance_projection",
        save_id="SAVE_01",
        season="2021-22",
    )
    view2 = data_service.query_role_view(query_coach_to_gm)
    assert view2.access_granted is False
    assert "ACCESS_DENIED" in view2.rejection_reason

    # 3. GM trying to read Coach tactical in-game playbook scheme
    query_gm_to_coach = RoleDataQuery(
        query_id="q-leak-03",
        requester_role=RoleType.GM,
        target_category="team_and_opponent_tactics",
        save_id="SAVE_01",
        season="2021-22",
    )
    view3 = data_service.query_role_view(query_gm_to_coach)
    assert view3.access_granted is False
    assert "ACCESS_DENIED" in view3.rejection_reason
