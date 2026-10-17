"""Serial benchmark phases borrow one outer lease without releasing its ownership."""

import os
import threading
from collections.abc import Callable

from evidence_rag.models.lease import LeaseHandle, ModelBusy, ModelLease, Owner


class BorrowedHandle(LeaseHandle):
    def __init__(self, owner: LeaseHandle, release: Callable[[], None]) -> None:
        super().__init__(owner.path, owner.token)
        self.release = release

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            self.release()


class BorrowedLease(ModelLease):
    def __init__(self, owner: LeaseHandle) -> None:
        super().__init__(owner.path)
        self.owner = owner
        self.slot = threading.BoundedSemaphore(1)

    def acquire(self, purpose: str) -> LeaseHandle:
        if not self.slot.acquire(blocking=False):
            raise ModelBusy()
        try:
            if self.owner.closed:
                raise RuntimeError("Benchmark lease owner has closed")
            stored = Owner.model_validate_json((self.owner.path / "owner.json").read_text())
            if stored.pid != os.getpid() or stored.token != self.owner.token:
                raise RuntimeError("Benchmark lease owner changed")
            return BorrowedHandle(self.owner, self.slot.release)
        except BaseException:
            self.slot.release()
            raise
