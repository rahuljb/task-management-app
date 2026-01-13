from accounts.permissions import is_superadmin, is_admin


def can_view_task_report(actor, task) -> bool:
    """
    SuperAdmin: can view all tasks
    Admin: can view tasks of users assigned to them
    """
    if is_superadmin(actor):
        return True

    if is_admin(actor):
        assignee_profile = getattr(task.assigned_to, "profile", None)
        return bool(assignee_profile and assignee_profile.assigned_admin_id == actor.id)

    return False
