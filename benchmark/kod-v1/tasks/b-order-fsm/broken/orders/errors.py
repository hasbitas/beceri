class TransitionError(Exception):
    """Base class of all errors raised for a rejected event."""


class InvalidTransition(TransitionError):
    def __init__(self, state, event):
        super().__init__(f"event {event!r} is not allowed in state {state!r}")
        self.state = state
        self.event = event


class RetryTooEarly(TransitionError):
    def __init__(self, retry_at):
        super().__init__(f"payment can be attempted again at {retry_at}")
        self.retry_at = retry_at


class ReturnWindowClosed(TransitionError):
    def __init__(self, deadline):
        super().__init__(f"returns were possible until {deadline}")
        self.deadline = deadline
