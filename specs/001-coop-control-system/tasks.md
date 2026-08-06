# Implementation Tasks: Poultry Coop Control System

This plan outlines the steps to implement the Poultry Coop Control System, with a focus on adding robust error handling and state management as defined in the specification.

## Phase 1: Foundational - Implement Door Error State

**Goal**: Update the core door control logic to handle hardware failures gracefully.

- [x] T001 [US1] Add `ERROR` to the `DoorState` enum in `chickenpi/door/door_driver.py`.
- [x] T002 [US1] Modify `DoorDriver.up()` and `DoorDriver.down()` in `chickenpi/door/door_driver.py` to check the return value of `wait_for_active()` and set state to `DoorState.ERROR` on timeout.
- [x] T003 [US5] Add a new `reset()` method to the `DoorDriver` class in `chickenpi/door/door_driver.py` that sets the state back to `DoorState.UNDEFINED`.
- [x] T004 [US5] Add a new `reset_door_state` function in `chickenpi/door/door.py` that calls the driver's new `reset` method.

## Phase 2: API - Expose Error Handling Endpoints

**Goal**: Integrate the new error handling logic into the FastAPI application.

- [x] T005 [US1] Update the `coop_door` endpoint in `chickenpi/chicken.py` to reject movement requests if the current door state is `DoorState.ERROR`.
- [x] T006 [US5] Add a new `POST /door/reset` endpoint in `chickenpi/chicken.py` that calls the `reset_door_state` function. This endpoint will require authentication.
- [x] T007 Modify the `read_temperature` endpoint in `chickenpi/chicken.py` to catch exceptions from `get_readings()` and return a `Temperature` model with `null` values as per `FR-003`.

## Phase 3: Testing - Verify Correctness

**Goal**: Add comprehensive tests for the new failure and recovery modes.

- [x] T008 [P] [US1] Add a unit test to `tests/test_door.py` that simulates a `wait_for_active` timeout and asserts that the `DoorDriver` state becomes `DoorState.ERROR`.
- [x] T009 [P] [US5] Add an API test to `tests/test_chicken.py` that forces the door into an error state, verifies movement is blocked, calls the `/door/reset` endpoint, and confirms controls are re-enabled.
- [x] T010 [P] Verify the initial `coop_door_state()` is `DoorState.UNDEFINED` upon application startup in `tests/test_door.py` to satisfy `FR-011`.
- [x] T011 [P] Add an API test to `tests/test_chicken.py` that mocks a `get_readings()` exception and asserts the `/temperature` endpoint returns a response with `null` values.

## Phase 4: Polish

**Goal**: Finalize logging and documentation.

- [x] T012 [P] Review all new logic and ensure critical state transitions (e.g., entering/resetting error state) are logged with appropriate severity in `chickenpi/door/door.py` and `chickenpi/chicken.py`.

## Dependencies & Execution

The implementation should proceed in phases. All tasks in a phase should be completed before moving to the next.

1.  **Phase 1 (Foundational)** must be completed first.
2.  **Phase 2 (API)** depends on Phase 1.
3.  **Phase 3 (Testing)** can be performed in parallel with Phases 1 and 2 if a TDD approach is taken, or after as a verification step. Tasks within Phase 3 are marked `[P]` as they are independent of each other.
4.  **Phase 4 (Polish)** is the final review step.

**MVP Scope**: Completing Phases 1, 2, and the relevant tests from Phase 3 (`T008`, `T009`) constitutes the minimum viable product for this feature enhancement.
