"""Explanatory entry point for one scheduled appointment reconciliation."""

from appointment_monitor import AppointmentSyncRequest, run_appointment_sync


def reconcile_appointment(request: AppointmentSyncRequest) -> None:
    """Stand in for the clinic scheduling system's successful sync."""
    print(f"reconciled appointment {request.appointment_id}")


if __name__ == "__main__":
    example = AppointmentSyncRequest(
        job_name="nightly-appointment-reconciliation",
        run_id="run-2026-08-19-clinic-17",
        clinic_id="clinic-17",
        appointment_id="appointment-2048",
    )
    decision = run_appointment_sync(example, reconcile_appointment)
    print(decision)

