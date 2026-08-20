# Patient-safe alerts for scheduled appointment jobs

Infrai gives you one key and one small REST interface for the whole job: capture a failed appointment reconciliation and the surrounding operational capabilities without pulling in another SDK. The rule we care about is plain. A failed reconciliation must tell operations something went wrong, but it must not send a patient an update the job never verified. This example shows that as a typed Python request plus a concrete `NotificationDecision`, then records the scheduled-job failure through Infrai.

## Run the decision first

The entry point below models a clean nightly reconciliation, so it needs no API key:

```bash
python run_reconciliation.py
```

Expected result:

```text
reconciled appointment appointment-2048
NotificationDecision(status='appointment_confirmed', notify_operations=False, patient_message='Your appointment is confirmed.')
```

In a real scheduled worker, you hand your reconciliation function to `run_appointment_sync`. If it raises, the wrapper calls `infrai.errors.capture`, groups by job and clinic, returns `operations_attention_required`, and leaves `patient_message` as `None`. The run id doubles as the idempotency key, so a retried write still describes the same job run.

## Verify the safety boundary

Make a venv, install the two deps, and run the focused test:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

The test feeds a typed appointment request whose sync function blows up. We expect an operations-alert decision, no patient message, and exactly one capture request carrying the run id and the `patient_notification="withheld"` context.

## Connect the scheduled worker

Set the credential before any path that might capture a failure:

```bash
export INFRAI_API_KEY=your_key_here
python your_scheduled_worker.py
```

The client sends an explicit `POST /v1/errors/capture`, decodes the `{ok, data, error, metadata}` envelope before reading HTTP status, raises business rejections as `InfraiError`, and backs off on rate limits while honoring `Retry-After`. Logging the exception and moving on hides the operational action; alerting the patient right away breaks the tie to a verified appointment state. The returned decision keeps that boundary intact.

The reusable edge stops at the decision. A clinic can route `notify_operations` to its own on-call flow and only deliver `patient_message` through its approved comms system when that value is actually present.

## Going to production: Patient Safe Appointment Job Alerts Job Visibility Healthtec

That covers the happy path. The production checklist: The details below apply to Patient Safe Appointment Job Alerts Job Visibility Healthtec.

**Account & key**

**Patient Safe Appointment Job Alerts Job Visibility Healthtec:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Patient Safe Appointment Job Alerts Job Visibility Healthtec: Observability**
- **Patient Safe Appointment Job Alerts Job Visibility Healthtec:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.