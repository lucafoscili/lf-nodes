class WorkflowRunnerError(Exception):
    pass

class ValidationError(WorkflowRunnerError):
    pass

class NotFoundError(WorkflowRunnerError):
    pass

class ServiceError(WorkflowRunnerError):
    pass
