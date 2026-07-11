# Living Logic — Student 5 Module

This module implements the governance, deployment, logging, and rollback layer for the Living Logic cyber-resilient ICS framework. It sits at the end of the pipeline, receiving adaptation decisions and managing everything from operator approval through to rollback handling and audit traceability.


# What this module does

1. Records anomaly and adaptation events in a persistent SQLite database
2. Manages the operator approval workflow before any adaptation is deployed
3. Tracks deployment state changes with full timestamps and operator IDs
4. Handles rollback triggering, reason logging, and outcome tracking
5. Exports event logs to CSV with optional filtering by severity, operator, or date range
6. Maintains a complete auditable history of all system changes
   

# Tech stack

Python
SQlite
Git / Github
Python logging library 


# Documentation

Full reference docs are in the docs/ folder:

1. logging_schema.md — explains every field in the database table
2. rollback_policy.md — defines when rollbacks are triggered and what gets logged
3. deployment_checklist.md — checklist for pre, during, and post deployment steps
