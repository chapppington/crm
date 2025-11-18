from dataclasses import dataclass
from uuid import UUID

from domain.base.entity import BaseEntity
from domain.organizations.value_objects.members import OrganizationMemberRoleValueObject


@dataclass(eq=False)
class OrganizationMemberEntity(BaseEntity):
    organization_id: UUID
    user_id: UUID
    role: OrganizationMemberRoleValueObject
