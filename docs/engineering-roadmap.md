# Operator pilot

## Current engineering work

Install a built wheel, configure a working-directory .env, run the controller on loopback and use synthetic events first. Inspect accepted/rejected requests and queue length in logs. Confirm token rejection, duplicate handling, queue limits and reconnect behavior before real use.

## Next operational acceptance

A named recurring operator workflow, allowed metadata, expected load and pilot end date. Record setup time, interventions and queue errors with units and a baseline. Restart empties in-memory state; confirm the operator recovery procedure before use. A synthetic replay is not adoption.

Implementation, automated checks and synthetic drills establish bounded behavior.
An operational record must separately identify the problem, requirements, exact
version/environment, deployment, upgrade/rollback, repeated use and measured outcome.
Those lifecycle fields are pending until actual use supplies evidence.

## Change and recovery

Extend this project before creating another repository for a related capability.
Add cloud hosting, infrastructure as code or monitoring only for a demonstrated
workload requirement. Preserve the previous version and configuration; reproduce
failures in a disposable environment, revert the scoped change if acceptance fails,
and record any lost in-memory state or required operator recovery. Never test
cleanup against personal data or publish raw host, customer or session records.
