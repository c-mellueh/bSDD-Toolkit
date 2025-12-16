
from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import os
import bsdd_gui
LOCK_SIZE = 1  # number of bytes to lock/unlock on Windows

if TYPE_CHECKING:
    from bsdd_gui.module.file_lock.prop import FileLockProperties


class FileLock:
    @classmethod
    def get_properties(cls) -> FileLockProperties:
        return bsdd_gui.FileLockProperties

           
    @classmethod
    def lock_file(cls, file_path: str) -> bool:
        """Try to acquire an exclusive lock for the given file path."""
        normalized_path = os.path.abspath(file_path)
        if cls.get_path() == normalized_path:
            logging.debug("Lock already held for %s", normalized_path)
            return True

        if not os.path.exists(normalized_path):
            logging.error("Cannot lock non-existent project file: %s", normalized_path)
            return False

        # Release a previous lock if we are switching files
        cls.unlock_file()

        try:
            cls.set_file(open(normalized_path, "a+"))
            cls._acquire_lock()
            cls.set_path(normalized_path)
            logging.info("Locked project file: %s", normalized_path)
            return True
        except Exception as exc:  # noqa: BLE001 - log and handle all lock errors
            logging.error("Unable to lock project file '%s': %s", normalized_path, exc)
            cls._cleanup()
            return False

    @classmethod
    def unlock_file(cls):
        """Release the current lock if held."""
        if cls.get_file() is None:
            return
        try:
            cls._release_lock()
            logging.info("Unlocked project file: %s", cls.get_path())
        except Exception as exc:  # noqa: BLE001 - log and handle all unlock errors
            logging.error("Error while unlocking project file '%s': %s", cls.get_path(), exc)
        finally:
            cls._cleanup()

    def _acquire_lock(cls):
        if os.name == "nt":
            import msvcrt

            # Lock the first byte; keep handle open so lock persists
            cls.get_file().seek(0)
            msvcrt.locking(cls.get_file().fileno(), msvcrt.LK_NBLCK, LOCK_SIZE)
        else:
            import fcntl

            fcntl.flock(cls.get_file(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _release_lock(cls):
        if cls.get_file() is None:
            return

        if os.name == "nt":
            import msvcrt

            cls.get_file().seek(0)
            msvcrt.locking(cls.get_file().fileno(), msvcrt.LK_UNLCK, LOCK_SIZE)
        else:
            import fcntl
            fcntl.flock(cls._file, fcntl.LOCK_UN)

    def _cleanup(cls):
        if cls.get_file():
            try:
                cls.get_file().close()
            except Exception:
                pass
        cls.set_file(None)
        cls.set_path(None)

    @classmethod
    def get_path(cls) -> str:
        props = cls.get_properties()
        return props.path

    @classmethod
    def set_path(cls,path: str):
        props = cls.get_properties()
        props.path = path

    @classmethod
    def get_file(cls):
        props = cls.get_properties()
        return props.file
    
    @classmethod
    def set_file(cls, file):
        props = cls.get_properties()
        props.file = file