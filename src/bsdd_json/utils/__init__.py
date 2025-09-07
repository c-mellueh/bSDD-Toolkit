def build_unique_code(base_name: str, existing_names: list[str]) -> str:
    if base_name not in existing_names:
        return base_name
    index = 2
    while True:
        new_name = f"{base_name}-{index}"
        if new_name not in existing_names:
            return new_name
        index += 1
