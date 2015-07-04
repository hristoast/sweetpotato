class SweetpotatoIOErrorBase(IOError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class BackupFileAlreadyExistsError(SweetpotatoIOErrorBase):
    """Raised when the target backup file already exists."""
    pass


class ConfFileError(SweetpotatoIOErrorBase):
    """
    Raised when a given conf file doesn't exist or have the right section.
    """
    pass


class EmptySettingError(SweetpotatoIOErrorBase):
    """Raised when a required setting value is None."""
    pass


class MissingExeError(SweetpotatoIOErrorBase):
    """Raised when a required executable is missing."""
    pass


class NoDirFoundError(SweetpotatoIOErrorBase):
    """Raised when a given directory does not exist."""
    pass


class NoJarFoundError(SweetpotatoIOErrorBase):
    """Raised when a given jar file does not exist."""
    pass


class ServerAlreadyRunningError(SweetpotatoIOErrorBase):
    """Raised when the configured server is already running."""
    pass


class ServerNotRunningError(SweetpotatoIOErrorBase):
    """Raised when the server is not running but was expected to be."""
    pass


class UnsupportedVersionError(SweetpotatoIOErrorBase):
    """
    Raised when we try to generate a server.properties
    for an unsupported mc_version.
    """
    pass
