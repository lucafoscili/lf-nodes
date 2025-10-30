"""Custom exceptions for workflow_runner.

Define a small set of domain exceptions that controllers translate into
HTTP responses.
"""

class WorkflowRunnerError(Exception):
    pass


class ValidationError(WorkflowRunnerError):
    pass


class NotFoundError(WorkflowRunnerError):
    pass


class ServiceError(WorkflowRunnerError):
    pass
