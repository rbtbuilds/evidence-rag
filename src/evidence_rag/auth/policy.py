from evidence_rag.contracts import Role


def can_read(role: Role, minimum: Role) -> bool:
    return role == "maintainer" or minimum == "reader"
