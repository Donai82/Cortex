class CortexError(Exception):
    """Base application error."""


class NotFoundError(CortexError):
    pass


class PolicyViolationError(CortexError):
    pass


class InvalidTransitionError(CortexError):
    pass


class ProviderError(CortexError):
    pass


class ProviderAuthenticationError(ProviderError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    pass


class ProviderHTTPError(ProviderError):
    pass


class ProviderMalformedResponseError(ProviderError):
    pass


class ProviderFailureError(ProviderError):
    pass
