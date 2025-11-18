from dataclasses import dataclass

from domain.base.entity import BaseEntity
from domain.organizations.value_objects.organizations import OrganizationNameValueObject


@dataclass(eq=False)
class OrganizationEntity(BaseEntity):
    name: OrganizationNameValueObject
