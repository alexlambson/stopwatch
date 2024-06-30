class ProgrammerError(Exception):
    """Raised when a programmer did something that is not allowed."""

    pass


class SkillIssue(ProgrammerError): ...
