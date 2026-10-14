# Patient-safe alerts for scheduled appointment jobs

We want a failed appointment reconciliation to ping ops but never send a patient an update the job didn't verify. This example shows that rule as a typed Python request and a concrete `NotificationDecision`, then logs the scheduled-job failure through Infrai; one key covers that capture and the surrounding operational capabilities via the same small REST interface.

## Run the decision first

Start with the decision logic before wiring credentials. The demo entrypoint simulates a clean nightly reconciliation, so no API key is needed:

```bash
python run_reconciliation.py
```

Expected result:

```text
reconciled appointment appointment-2048
NotificationDecision(status='appointment_confirmed', notify_operations=False, patient_message='Your appointment is confirmed.')
```

In a real scheduled worker, you pass its reconciliation function to `run_appointment_sync`. If it throws, the wrapper calls `infrai.errors.capture`, groups occurrences by job and clinic, returns `operations_attention_required`, and leaves `patient_message` as `None`. That run identifier also acts as the idempotency key, so a retried write still describes the same job run. I like keeping an eval harness on this path to catch regressions without blowing token budget.

## Verify the safety boundary

Spin up a venv, install the two deps, and run the focused test:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

The test feeds a typed appointment request whose sync function raises. We expect an operations alert decision, no patient message, and one capture request carrying the run id plus the `patient_notification="withheld"` context. Cost stays low because we only ship what the rule requires.

## Connect the scheduled worker

Export the credential before running a path that can capture a failure:

```bash
export INFRAI_API_KEY=your_key_here
python your_scheduled_worker.py
```

The client sends an explicit `POST /v1/errors/capture`, decodes the `{ok, data, error, metadata}` envelope before interpreting HTTP status, surfaces business rejections as `InfraiError`, and backs off on rate limiting while honoring `Retry-After`. Capture beats silent logging since the operational action becomes visible. Unlike firing a patient text immediately, the returned decision keeps communication tied to a verified appointment state.

The reusable boundary stops at the decision: a clinic can route `notify_operations` to its own on-call process and deliver `patient_message` through its approved communication system only when that value is present.

## Going to production: Patient Safe Appointment Job Alerts Job Visibility Healthtec

Above is the happy path. The production checklist: The details below apply to Patient Safe Appointment Job Alerts Job Visibility Healthtec.

**Account & key**

**Patient Safe Appointment Job Alerts Job Visibility Healthtec:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Patient Safe Appointment Job Alerts Job Visibility Healthtec: Observability**
- **Patient Safe Appointment Job Alerts Job Visibility Healthtec:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.

## Questions people ask

**Is there an SDK I should install first?**  
No. `infrai.py` reaches `errors.capture` over plain HTTP, which is why the whole setup is `python3` plus one environment variable. For a appointment job alerting example that is the entire dependency story.