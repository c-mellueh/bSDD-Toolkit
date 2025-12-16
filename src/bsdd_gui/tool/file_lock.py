from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import os
import getpass
from datetime import datetime
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.file_lock.prop import FileLockProperties


class FileLock:
    @classmethod
    def get_properties(cls) -> FileLockProperties:
        return bsdd_gui.FileLockProperties

    @classmethod
    def build_lockpath(cls, file_path: str) -> str:
        """Build the lock file path for a given file path."""
        return f"{os.path.abspath(file_path)}.lock"

    @classmethod
    def lock_file(cls, file_path: str) -> bool:
        """Try to acquire an exclusive lock marker for the given file path."""
        normalized_path = os.path.abspath(file_path)
        if cls.get_path() == normalized_path:
            logging.debug("Lock already held for %s", normalized_path)
            return True

        if not os.path.exists(normalized_path):
            logging.error("Cannot lock non-existent project file: %s", normalized_path)
            return False

        # Release a previous lock if we are switching files
        cls.unlock_file()

        lock_path = cls.build_lockpath(normalized_path)

        try:
            file = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(file, cls._build_lock_contents())
            cls.set_file(file)
            cls.set_path(normalized_path)
            cls.set_lock_path(lock_path)
            logging.info("Locked project file via %s", lock_path)
            return True
        except FileExistsError:
            logging.info("Project file already locked: %s", normalized_path)
            cls._cleanup()
            return False
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
            os.close(cls.get_file())
            if cls.get_lock_path() and os.path.exists(cls.get_lock_path()):
                os.remove(cls.get_lock_path())
            logging.info("Unlocked project file: %s", cls.get_path())
        except Exception as exc:  # noqa: BLE001 - log and handle all unlock errors
            logging.error("Error while unlocking project file '%s': %s", cls.get_path(), exc)
        finally:
            cls.set_file(None)
            cls._cleanup()

    @classmethod
    def overwrite_lock(cls, file_path: str):
        lock_path = cls.build_lockpath(file_path)
        try:
            os.remove(lock_path)
            logging.info("Removed existing lock file: %s", lock_path)
            cls.lock_file(file_path)
        except Exception as exc:
            logging.info("Unable to remove existing lock file '%s': %s", lock_path, exc)
            cls.set_lock_path(lock_path)
            cls.set_path(file_path)

    @classmethod
    def _cleanup(cls):
        if cls.get_file() is not None:
            try:
                os.close(cls.get_file())
            except Exception:
                pass
        cls.set_file(None)
        cls.set_path(None)
        cls.set_lock_path(None)

    @classmethod
    def _build_lock_contents(cls) -> bytes:
        """Return the contents to be written into the lock file."""
        try:
            username = getpass.getuser()
        except Exception:
            username = os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"
        lock_time = datetime.now().isoformat()
        content = f"pid:{os.getpid()} locked by {username} at {lock_time}"
        return content.encode("ascii", "ignore")

    @classmethod
    def get_path(cls) -> str:
        props = cls.get_properties()
        return props.path

    @classmethod
    def set_path(cls, path: str):
        props = cls.get_properties()
        props.path = path

    @classmethod
    def get_file(cls):
        props = cls.get_properties()
        return props.file

    @classmethod
    def set_file(cls, file: int | None):
        props = cls.get_properties()
        props.file = file

    @classmethod
    def get_lock_path(cls) -> str:
        props = cls.get_properties()
        return props.lock_path

    @classmethod
    def set_lock_path(cls, lock_path: str | None):
        props = cls.get_properties()
        props.lock_path = lock_path
