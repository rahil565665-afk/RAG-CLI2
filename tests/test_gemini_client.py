from app.gemini_client import GeminiProviderError


class FakeSdkError(Exception):
    def __init__(self, code, status=None):
        super().__init__("simulated provider failure; no credentials are included")
        self.code = code
        self.status = status


def test_rate_limit_error_is_distinguished_from_generic_provider_failure():
    error = GeminiProviderError.from_exception(FakeSdkError(429, "RESOURCE_EXHAUSTED"))
    assert error.error_code == "GEMINI_RATE_LIMITED"
    assert error.status_code == 429
    assert "quota" in str(error).lower()


def test_temporary_unavailable_error_has_retry_guidance():
    error = GeminiProviderError.from_exception(FakeSdkError(503, "UNAVAILABLE"))
    assert error.error_code == "GEMINI_TEMPORARILY_UNAVAILABLE"
    assert error.status_code == 503
    assert "automatic retries" in str(error).lower()


def test_invalid_request_is_not_mislabelled_as_transient():
    error = GeminiProviderError.from_exception(FakeSdkError(400, "INVALID_ARGUMENT"))
    assert error.error_code == "GEMINI_INVALID_REQUEST"
    assert error.status_code == 400


def test_timeout_is_reported_as_network_error():
    error = GeminiProviderError.from_exception(TimeoutError("request timed out"))
    assert error.error_code == "GEMINI_NETWORK_ERROR"
