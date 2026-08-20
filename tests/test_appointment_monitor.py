from unittest.mock import patch

from appointment_monitor import AppointmentSyncRequest, run_appointment_sync


def test_failed_sync_alerts_operations_and_withholds_patient_message() -> None:
    request = AppointmentSyncRequest(
        job_name="nightly-appointment-reconciliation",
        run_id="run-42",
        clinic_id="clinic-17",
        appointment_id="appointment-2048",
    )

    def failed_sync(_: AppointmentSyncRequest) -> None:
        raise ValueError("source record is incomplete")

    with patch("appointment_monitor.infrai.errors.capture") as capture:
        decision = run_appointment_sync(request, failed_sync)

    assert decision.status == "operations_attention_required"
    assert decision.notify_operations is True
    assert decision.patient_message is None
    capture.assert_called_once()
    assert capture.call_args.kwargs["idempotency_key"] == "run-42"
    assert capture.call_args.kwargs["context"]["patient_notification"] == "withheld"

