from enum import Enum


class ProductStatus(str, Enum):
    DRAFT = "Draft"
    SUBMIT = "Submit"
    LOCKED = "Locked"
