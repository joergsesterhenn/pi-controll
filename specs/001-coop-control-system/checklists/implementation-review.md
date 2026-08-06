# Implementation Checklist: Poultry Coop Control System

**Purpose**: A checklist for the developer (me) to verify that the implementation meets all functional and safety requirements before handing off for review.
**Created**: 2026-02-22
**Feature**: [spec.md](../spec.md)

## Core Functionality
- [x] CHK001 - **Door Control**: Verify that `POST /door` requests correctly trigger the `open_door` and `close_door` functions and that the physical (or mock) motor responds as expected. [Spec §FR-001]
- [x] CHK002 - **Light Control**: Confirm that `POST /light` toggles the light state and `GET /light/state` accurately reflects it. [Spec §FR-004]
- [x] CHK003 - **Image Capture**: Verify that `POST /image` triggers a capture and `GET /image` returns the latest image file. [Spec §FR-002]
- [x] CHK004 - **Temperature Reading**: Confirm that `GET /temperature` returns current sensor data. [Spec §FR-003]
- [x] CHK005 - **Authentication**: Test that all hardware-related endpoints return a 401/403 error if the Firebase authentication token is missing or invalid. [Spec §FR-006]

## Error Handling & State Management
- [x] CHK006 - **Door Timeout**: Induce a motor timeout (e.g., by disconnecting a mock sensor) and verify the door state transitions to `ERROR`. [Spec §FR-008]
- [x] CHK007 - **Error State Lockout**: While the door is in the `ERROR` state, confirm that any new requests to move the door are rejected with an appropriate error code. [Spec §FR-009]
- [x] CHK008 - **Manual Reset**: After inducing an error, verify that the `POST /door/reset` endpoint successfully clears the `ERROR` state and re-enables door controls. [Spec §FR-010]
- [x] CHK009 - **Sensor Failure**: Simulate a temperature sensor failure and verify the `/temperature` endpoint returns `null` for the temperature fields. [Spec §FR-003]
- [x] CHK010 - **Startup State**: Restart the application and verify that the initial door state is reported as `UNDEFINED` before any sensor has been triggered. [Spec §FR-011]
- [x] CHK011 - **Invalid Commands**: Send invalid data to endpoints (e.g., `POST /door` with a direction other than "up" or "down") and confirm a 4xx error is returned.

## Testing & Validation
- [x] CHK012 - **Unit Tests**: Confirm that new unit tests have been written for the new error handling and state logic.
- [x] CHK013 - **Integration Tests**: Ensure integration tests are added to simulate the full flow of a command from the API endpoint to the mock hardware driver, including failure scenarios.
- [x] CHK014 - **Code Review**: Ensure all new code adheres to the project's style guide and the principles in the constitution.
