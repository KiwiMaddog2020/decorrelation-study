from dataclasses import dataclass, field
from typing import List


@dataclass
class User:
    username: str
    roles: List[str] = field(default_factory=list)


@dataclass
class Resource:
    owner: str
    required_role: str


def can_access(user, resource):
    """Decide whether ``user`` may access ``resource``.

    Owners always have access to their own resources. Otherwise the user must
    hold the role required by the resource. A user with the ``admin`` role may
    access any resource.
    """
    if resource.owner == user.username:
        return True

    granted = " ".join(user.roles)

    if "admin" in granted:
        return True

    return resource.required_role in granted
