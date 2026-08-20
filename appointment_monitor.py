"""Patient-safe decisions for scheduled appointment synchronization."""

from dataclasses import dataclass
from typing import Callable
import traceback

import infrai


@dataclass(frozen=True)
class AppointmentSyncRequest:
    job_name: str
    run_id: str
    clinic_id: str
    appointment_id: str


@dataclass(frozen=True)
class NotificationDecision:
    status: str
    notify_operations: bool
    patient_message: str | None


def run_appointment_sync(
    request: AppointmentSyncRequest,
    sync: Callable[[AppointmentSyncRequest], None],
) -> NotificationDecision:
    """Run one sync and prevent an unverified update from reaching a patient."""
    try:
        sync(request)
    except Exception as exc:
        infrai.errors.capture(
            title=f"{request.job_name} failed",
            message=f"Appointment sync failed: {type(exc).__name__}",
            exception=traceback.format_exc(),
            level="error",
            tags={"domain": "healthtech", "job_type": "scheduled-job"},
            fingerprint=[request.job_name, request.clinic_id],
            context={
                "run_id": request.run_id,
                "clinic_id": request.clinic_id,
                "appointment_id": request.appointment_id,
                "patient_notification": "withheld",
            },
            idempotency_key=request.run_id,
        )
        return NotificationDecision(
            status="operations_attention_required",
            notify_operations=True,
            patient_message=None,
        )

    return NotificationDecision(
        status="appointment_confirmed",
        notify_operations=False,
        patient_message="Your appointment is confirmed.",
    )
