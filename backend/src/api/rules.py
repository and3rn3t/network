"""Alert Rules API endpoints."""

import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.middleware.error_handler import NotFoundError
from backend.src.services.database_service import get_database
from src.alerts.models import AlertRule
from src.database.database import Database
from src.database.repositories.alert_rule_repository import AlertRuleRepository

router = APIRouter()


@router.get("")
async def list_rules(
    enabled_only: bool = Query(False, description="Show only enabled rules"),
    host_id: Optional[int] = Query(None, description="Filter by host ID"),
    db: Database = Depends(get_database),
):
    """
    List all alert rules.

    Returns list of rules with optional filtering.
    """
    rule_repo = AlertRuleRepository(db)

    if host_id:
        rules = rule_repo.get_by_host(host_id)
    else:
        rules = rule_repo.get_all(enabled_only=enabled_only)

    return {
        "rules": [rule.to_dict() for rule in rules],
        "count": len(rules),
    }


@router.get("/{rule_id}")
async def get_rule(
    rule_id: int,
    db: Database = Depends(get_database),
):
    """
    Get rule details by ID.

    Returns complete rule configuration.
    """
    rule_repo = AlertRuleRepository(db)
    rule = rule_repo.get_by_id(rule_id)

    if not rule:
        raise NotFoundError(f"Rule with ID {rule_id} not found")

    return rule.to_dict()


@router.post("")
async def create_rule(
    rule_data: dict = Body(...),
    db: Database = Depends(get_database),
):
    """
    Create a new alert rule.

    Accepts rule configuration and creates a new monitoring rule.
    """
    rule_repo = AlertRuleRepository(db)

    # Convert to AlertRule object
    rule = AlertRule.from_dict(rule_data)
    created_rule = rule_repo.create(rule)

    return {
        "success": True,
        "rule": created_rule.to_dict(),
    }


@router.put("/{rule_id}")
async def update_rule(
    rule_id: int,
    rule_data: dict = Body(...),
    db: Database = Depends(get_database),
):
    """
    Update an existing alert rule.

    Updates rule configuration.
    """
    rule_repo = AlertRuleRepository(db)
    existing_rule = rule_repo.get_by_id(rule_id)

    if not existing_rule:
        raise NotFoundError(f"Rule with ID {rule_id} not found")

    # Update with new data
    rule_data["id"] = rule_id
    updated_rule = AlertRule.from_dict(rule_data)
    rule_repo.update(updated_rule)

    return {
        "success": True,
        "rule": updated_rule.to_dict(),
    }


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: Database = Depends(get_database),
):
    """
    Delete an alert rule.

    Removes the rule from the system.
    """
    rule_repo = AlertRuleRepository(db)
    success = rule_repo.delete(rule_id)

    if not success:
        raise NotFoundError(f"Rule with ID {rule_id} not found")

    return {
        "success": True,
        "rule_id": rule_id,
    }


@router.post("/{rule_id}/enable")
async def enable_rule(
    rule_id: int,
    db: Database = Depends(get_database),
):
    """
    Enable an alert rule.

    Activates the rule for monitoring.
    """
    rule_repo = AlertRuleRepository(db)
    rule = rule_repo.get_by_id(rule_id)

    if not rule:
        raise NotFoundError(f"Rule with ID {rule_id} not found")

    # Update enabled status
    rule_dict = rule.to_dict()
    rule_dict["enabled"] = True
    updated_rule = AlertRule.from_dict(rule_dict)
    rule_repo.update(updated_rule)

    return {
        "success": True,
        "rule_id": rule_id,
        "enabled": True,
    }


@router.post("/{rule_id}/disable")
async def disable_rule(
    rule_id: int,
    db: Database = Depends(get_database),
):
    """
    Disable an alert rule.

    Deactivates the rule from monitoring.
    """
    rule_repo = AlertRuleRepository(db)
    rule = rule_repo.get_by_id(rule_id)

    if not rule:
        raise NotFoundError(f"Rule with ID {rule_id} not found")

    # Update enabled status
    rule_dict = rule.to_dict()
    rule_dict["enabled"] = False
    updated_rule = AlertRule.from_dict(rule_dict)
    rule_repo.update(updated_rule)

    return {
        "success": True,
        "rule_id": rule_id,
        "enabled": False,
    }
