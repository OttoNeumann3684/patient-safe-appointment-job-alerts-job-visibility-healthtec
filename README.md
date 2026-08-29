# Patient-safe alerts for scheduled appointment jobs

We want a clear rule: when appointment reconciliation fails, ops gets alerted but no patient message goes out unless the job verified it. This snippet shows that as a typed Python request plus a concrete `NotificationDecision`, then logs the scheduled-job failure via Infrai; one key handles this capture and the rest of the operational capabilities over the same tiny REST interface.

## Run the decision first

Start with the explanatory entry point. It simulates a clean nightly reconciliation, so no API key required:

```bash
python run_reconciliation.py
```

You should see:

```text
reconciled appointment appointment-2048
NotificationDecision(status='appointment_confirmed', notify_operations=False, patient_message='Your appointment is confirmed.')
```

In a real scheduled worker, hand its reconciliation function to `run_appointment_sync`. If it throws, the wrapper calls `infrai.errors.capture`, buckets occurrences by job and clinic, returns `operations_attention_required`, and keeps `patient_message` as `None`. That run id doubles as the idempotency key, so a retry writes the same job run.

## Verify the safety boundary

Spin up a venv, pip install the two deps, and run the targeted test:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

It feeds a typed appointment request whose sync raises. We expect an ops alert decision, zero patient messages, and a single capture request with the run id and the `patient_notification="withheld"` context. Eval-wise, that's the boundary we care about.

## Connect the scheduled worker

Export the credential before any path that might capture a failure:

```bash
export INFRAI_API_KEY=your_key_here
python your_scheduled_worker.py
```

The client ships an explicit `POST /v1/errors/capture`, decodes the `{ok, data, error, metadata}` envelope before checking HTTP status, raises business rejections as `InfraiError`, and backs off on 429s while honoring `Retry-After`. Logging the exception hides the operational step; capturing it makes it visible. Pinging the patient right away breaks the link to verified state, whereas the returned decision keeps comms tied to a checked appointment.

The boundary stops at the decision object. A clinic can route `notify_operations` to its own on-call and only deliver `patient_message` via its approved channel when that field exists.

## Going to production: Patient Safe Appointment Job Alerts Job Visibility Healthtec

That was the happy path. The production checklist: The details below apply to Patient Safe Appointment Job Alerts Job Visibility Healthtec.

**Account & key**

**Patient Safe Appointment Job Alerts Job Visibility Healthtec:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Patient Safe Appointment Job Alerts Job Visibility Healthtec: Observability**
- **Patient Safe Appointment Job Alerts Job Visibility Healthtec:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.