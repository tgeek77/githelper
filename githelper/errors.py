"""Error types and subprocess helpers."""


class GithelperError(Exception):
    """Raised when a githelper operation fails."""

    def __init__(self, message, stderr=None, returncode=1):
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


def format_subprocess_error(exc):
    """Format a CalledProcessError with stderr when available."""
    msg = str(exc)
    stderr = getattr(exc, "stderr", None)
    if stderr and stderr.strip():
        msg = f"{msg}\n{stderr.strip()}"
    return msg
