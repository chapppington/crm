from uuid import UUID

from pydantic import BaseModel

from domain.organizations.entities import (
    OrganizationEntity,
    OrganizationMemberEntity,
)


class OrganizationResponseSchema(BaseModel):
    id: UUID
    name: str
    created_at: str

    @classmethod
    def from_entity(cls, entity: OrganizationEntity) -> "OrganizationResponseSchema":
        return cls(
            id=entity.oid,
            name=entity.name.as_generic_type(),
            created_at=entity.created_at.isoformat() if entity.created_at else "",
        )


class OrganizationMemberResponseSchema(BaseModel):
    organization_id: UUID
    role: str
    organization: OrganizationResponseSchema | None = None

    @classmethod
    def from_entity(
        cls,
        member: OrganizationMemberEntity,
        organization: OrganizationEntity | None = None,
    ) -> "OrganizationMemberResponseSchema":
        return cls(
            organization_id=member.organization_id,
            role=member.role.as_generic_type().value,
            organization=OrganizationResponseSchema.from_entity(organization) if organization else None,
        )


class GetUserOrganizationsResponseSchema(BaseModel):
    organizations: list[OrganizationMemberResponseSchema]


class CreateOrganizationRequestSchema(BaseModel):
    name: str
