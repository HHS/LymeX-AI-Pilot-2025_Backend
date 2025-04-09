from enum import Enum


class CompanyRoles(str, Enum):
    ADMINISTRATOR = "Administrator"
    CONTRIBUTOR = "Contributor"
    VIEWER = "Viewer"
    GUEST = "Guest"
    SUPERUSER = "SuperUser"


COMPANY_ROLES_ORDER = {
    CompanyRoles.SUPERUSER: 0,
    CompanyRoles.ADMINISTRATOR: 1,
    CompanyRoles.CONTRIBUTOR: 2,
    CompanyRoles.VIEWER: 3,
    CompanyRoles.GUEST: 4,
}


class CompanyMemberStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    INVITED = "Invited"