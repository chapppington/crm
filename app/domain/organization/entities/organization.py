from dataclasses import dataclass

from domain.base.entity import BaseEntity
from domain.organization.value_objects.organization import OrganizationNameValueObject


@dataclass(eq=False)
class OrganizationEntity(BaseEntity):
    name: OrganizationNameValueObject
