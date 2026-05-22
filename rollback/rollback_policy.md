# Rollback Policy — Living Logic

## Trigger conditions
A rollback is triggered when:
- adaptation causes another anomaly,
- pressure/temperature exceeds threshold,
- operator manually triggers rollback.

## Rollback steps
1. Halt adaptation
2. Restore previous system state
3. Log rollback event
4. Notify operator

## Rollback status values
- SUCCESS
- FAILED
- PARTIAL