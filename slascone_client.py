"""Python bindings for the SlasconeClient C ABI."""

from ctypes import CDLL, c_char_p, c_int, c_uint32, c_void_p
from enum import IntEnum
from os import PathLike, fspath
from pathlib import Path
from threading import Lock
from types import TracebackType
from typing import Never
from weakref import finalize


_DEFAULT_LIBRARY = Path(__file__).resolve().parent / "slascone-client" / "SlasconeClient.so"
_ABI_VERSION = 1


class SlasconeStatus(IntEnum):
    OK = 0
    INVALID_ARGUMENT = 1
    OUT_OF_MEMORY = 2
    INTERNAL_ERROR = 3
    NOT_CONFIGURED = 4
    INVALID_PUBLIC_KEY = 5
    FILE_ERROR = 6
    INVALID_XML = 7
    INVALID_SIGNATURE = 8
    LICENSE_KEY_MISMATCH = 9
    REVISION_MISMATCH = 10
    CLIENT_ID_MISMATCH = 11
    RELEASE_NOT_ALLOWED = 12
    INVALID_LICENSE_DATES = 13
    LICENSE_NOT_YET_VALID = 14
    LICENSE_EXPIRED = 15


def _encode(value: str) -> bytes:
    if "\0" in value:
        raise ValueError("Slascone strings cannot contain NUL characters")
    return value.encode("utf-8")


class SlasconeClient:
    """Own a native client. Use a with block or call close() to release it.

    The default library is the bundled Linux .so. Pass library_path to use
    another ABI-compatible build. Operations return the native SlasconeStatus.
    """

    def __init__(
        self, product_id: str, *, library_path: str | PathLike[str] = _DEFAULT_LIBRARY
    ) -> None:
        product = _encode(product_id)
        path = Path(library_path).resolve()
        library = CDLL(str(path))
        library.slascone_client_abi_version.argtypes = []
        library.slascone_client_abi_version.restype = c_uint32
        self._abi_version = library.slascone_client_abi_version()
        if self._abi_version != _ABI_VERSION:
            raise RuntimeError(
                f"Unsupported Slascone ABI version {self._abi_version} in {path}; "
                f"expected {_ABI_VERSION}"
            )

        library.client_create.argtypes = [c_char_p]
        library.client_create.restype = c_void_p
        library.client_destroy.argtypes = [c_void_p]
        library.client_destroy.restype = None
        for setter in (library.set_client_id, library.set_software_release, library.set_pem_key):
            setter.argtypes = [c_void_p, c_char_p]
            setter.restype = c_int
        library.check_offline_license.argtypes = [c_void_p, c_char_p, c_char_p]
        library.check_offline_license.restype = c_int

        self._library = library
        self._lock = Lock()
        self._handle = library.client_create(product)
        if self._handle is None:
            raise MemoryError("Slascone client allocation failed")
        self._finalizer = finalize(self, library.client_destroy, self._handle)

    @property
    def abi_version(self) -> int:
        """Return the loaded library's ABI version."""
        return self._abi_version

    def _open_handle(self) -> int:
        if not self._finalizer.alive:
            raise RuntimeError("Slascone client is closed")
        return self._handle

    def set_client_id(self, value: str) -> SlasconeStatus:
        """Set the client ID; an empty string clears it."""
        with self._lock:
            return SlasconeStatus(self._library.set_client_id(self._open_handle(), _encode(value)))

    def set_software_release(self, value: str) -> SlasconeStatus:
        """Set the software release; an empty string clears it."""
        with self._lock:
            return SlasconeStatus(
                self._library.set_software_release(self._open_handle(), _encode(value))
            )

    def set_pem_key(self, value: str) -> SlasconeStatus:
        """Set the PEM public key; an empty string clears it."""
        with self._lock:
            return SlasconeStatus(self._library.set_pem_key(self._open_handle(), _encode(value)))

    def check_offline_license(
        self,
        license_path: str | PathLike[str],
        activation_path: str | PathLike[str] | None = None,
    ) -> SlasconeStatus:
        """Check a license file. None or an empty activation path selects inline activation."""
        with self._lock:
            return SlasconeStatus(
                self._library.check_offline_license(
                    self._open_handle(),
                    _encode(fspath(license_path)),
                    None if activation_path is None else _encode(fspath(activation_path)),
                )
            )

    def close(self) -> None:
        """Release the handle. Closing more than once is safe."""
        with self._lock:
            self._finalizer()

    def __enter__(self) -> "SlasconeClient":
        with self._lock:
            self._open_handle()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __reduce_ex__(self, _protocol: int) -> Never:
        raise TypeError("SlasconeClient handles cannot be copied or pickled")
