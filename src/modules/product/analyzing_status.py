from enum import Enum


class AnalyzingStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In_Progress"
    COMPLETED = "Completed"
