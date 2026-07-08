from dataclasses import dataclass, field


VALID_PRIORITIES = {"P0", "P1", "P2"}
DEFAULT_OWNER = "woyexiaole"


@dataclass(frozen=True)
class TestMetadata:
    module: str
    priority: str
    owner: str = DEFAULT_OWNER
    feature: str = ""
    description: str = ""
    tags: tuple = field(default_factory=tuple)

    def to_dict(self):
        tags = _merge_tags(self.tags, (self.module, self.priority))
        return {
            "module": self.module,
            "priority": self.priority,
            "owner": self.owner,
            "feature": self.feature,
            "description": self.description,
            "tags": tags,
        }


def _merge_tags(*tag_groups):
    merged_tags = []
    seen_tags = set()
    for tag_group in tag_groups:
        for tag in tag_group:
            normalized_tag = str(tag).lower()
            if normalized_tag in seen_tags:
                continue
            merged_tags.append(str(tag))
            seen_tags.add(normalized_tag)
    return merged_tags


def metadata(
    module,
    priority,
    owner=DEFAULT_OWNER,
    feature="",
    description="",
    tags=None,
):
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Expected one of: P0, P1, P2.")

    metadata_value = TestMetadata(
        module=module,
        priority=priority,
        owner=owner,
        feature=feature,
        description=description,
        tags=tuple(tags or ()),
    )

    def decorator(test_func):
        test_func.__test_metadata__ = metadata_value
        return test_func

    return decorator


def get_metadata(test_func):
    metadata_value = getattr(test_func, "__test_metadata__", None)
    if metadata_value is None:
        return None
    return metadata_value.to_dict()


def get_metadata_from_test(test_case):
    method = getattr(test_case, test_case._testMethodName)
    return get_metadata(method)
