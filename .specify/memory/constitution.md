# ChickenPi Constitution

## Core Principles

### I. Device-Oriented Architecture
The system is built around physical and logical devices (Door, Light, Temperature, Image). Each device must have a clear separation between its business logic and the hardware driver implementation.

### II. Hardware Abstraction
All hardware interactions (GPIO, sensors, camera) must be abstracted. The application should be able to run in a simulated environment (e.g., development machine) by providing mock or factory-generated device instances.

### III. Security-First (Firebase Auth)
All REST endpoints that control or read from the coop must be protected by Firebase Authentication. No sensitive operation shall be performed without a valid, verified Firebase token.

### IV. Observability & Logging
The system must maintain high observability. Every request, hardware state change, and exception must be logged using structured JSON logging. Sentry integration is mandatory for error tracking in production.

### V. FastAPI & REST Standards
The backend must follow modern FastAPI practices, including the use of Dependency Injection for authentication and lifespan events for resource management. Endpoints should be concise and adhere to RESTful principles.

## Technical Stack & Constraints

- **Language**: Python >= 3.12
- **Web Framework**: FastAPI with Uvicorn
- **Authentication**: Firebase Admin SDK
- **Hardware Control**: `gpiozero`, `rpi-lgpio` (specifically for Raspberry Pi 2b/3/4 compatibility)
- **Monitoring**: Sentry SDK, `python-json-logger`
- **Deployment**: Raspberry Pi 2b (target hardware), Caddy as reverse proxy

## Development Workflow

- **Testing**: `pytest` is used for all tests. Test coverage should include both logic and API endpoints.
- **Environment**: Support for local development (non-Pi hardware) must be maintained via the device factory pattern.
- **Linting/Style**: Adhere to PEP 8. Use `noqa` sparingly and only for justified cases (e.g., circular imports or specific logging setups).

## Governance

This constitution supersedes individual feature plans. Any architectural deviation must be justified and documented. Changes to the core tech stack or security model require a formal amendment.

**Version**: 1.0.0 | **Ratified**: 2026-02-22 | **Last Amended**: 2026-02-22
