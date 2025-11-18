from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from domain.organizations.entities import OrganizationMemberEntity
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import ContactEntity


def check_contact_access(
    contact: ContactEntity,
    member: OrganizationMemberEntity,
    user_id: UUID,
) -> None:
    """Проверка прав доступа к контакту."""
    role = member.role.as_generic_type()

    # owner/admin/manager могут работать со всеми контактами
    if role in {OrganizationMemberRole.OWNER, OrganizationMemberRole.ADMIN, OrganizationMemberRole.MANAGER}:
        return

    # member может работать только со своими контактами
    if role == OrganizationMemberRole.MEMBER:
        if contact.owner_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own contacts",
            )


def check_contact_organization(
    contact: ContactEntity,
    organization_id: UUID,
) -> None:
    """Проверка, что контакт принадлежит организации."""
    if contact.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )


def can_filter_by_owner(member: OrganizationMemberEntity) -> bool:
    """Проверка, может ли пользователь фильтровать по owner_id."""
    role = member.role.as_generic_type()
    return role in {OrganizationMemberRole.OWNER, OrganizationMemberRole.ADMIN, OrganizationMemberRole.MANAGER}
