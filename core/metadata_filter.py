def filter_metadata_by_role(metadata: dict, role: str) -> dict:
    filtered = {}
    for sheet, cols in metadata.items():
        allowed = [col for col in cols if role in col.get("access_roles", [])]
        if allowed:
            filtered[sheet] = allowed
    return filtered
