# Implementation Plan: Poultry Coop Control System

**Branch**: `001-coop-control-system` | **Date**: 2026-02-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-coop-control-system/spec.md`

## Summary

Build a Raspberry Pi-based backend to control a poultry coop's door, lighting, and environmental monitoring. The system will expose a FastAPI REST API protected by Firebase Authentication (OAuth2/JWT). The technical approach leverages a Device-Oriented Architecture with hardware abstraction to support both physical Pi hardware (GPIO, PiCamera) and simulated environments for development and testing.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Firebase Admin SDK, gpiozero, rpi-lgpio, python-json-logger, sentry-sdk  
**Storage**: Local file system for webcam captures, Firebase Realtime Database for historical temperature data (as per README.md)  
**Testing**: pytest (unit, integration, and contract tests)  
**Target Platform**: Raspberry Pi 2b (Linux)  
**Project Type**: Web Service / IoT Backend  
**Performance Goals**: REST request initiation < 500ms, Image delivery < 5s  
**Constraints**: Must run on low-resource Raspberry Pi 2b; strictly authenticated via Firebase; reliable GPIO state management.  
**Scale/Scope**: Single coop installation; multiple authorized users.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Device-Oriented Architecture**: PASSED - Implementation will follow existing `door`, `light`, `temperature` module patterns.
- **Hardware Abstraction**: PASSED - Using `device/factory.py` to handle hardware/mock injection.
- **Security-First**: PASSED - Firebase token verification is required for all control endpoints.
- **Observability**: PASSED - Structured logging and Sentry are already integrated in `chicken.py`.
- **FastAPI Standards**: PASSED - Utilizing FastAPI lifespan and dependency injection.

## Project Structure

### Documentation (this feature)

```text
specs/001-coop-control-system/
├── plan.md              # This file
├── research.md          # Hardware compatibility and GPIO mapping
├── data-model.md        # API schemas and internal state models
├── quickstart.md        # Setup guide for the Pi 2b
├── contracts/           # API request/response specifications
└── checklists/
    └── requirements.md  # Quality validation
```

### Source Code (repository root)

```text
chickenpi/
├── auth/                # Firebase authentication logic
├── device/              # Device factory and hardware abstraction
├── door/                # Door logic and GPIO driver
├── image/               # Webcam capture and storage
├── light/               # Lighting control and GPIO driver
├── logging/             # Structured JSON logging configuration
├── temperature/         # W1 sensor reading logic
└── chicken.py           # FastAPI application and route definitions

tests/
├── test_door.py
├── test_image.py
├── test_light.py
├── test_temperature.py
└── test_chicken.py      # Integration/Contract tests
```

**Structure Decision**: Single project structure (Option 1). The project is already organized into clear domain-specific modules within the `chickenpi/` package, which aligns perfectly with the Device-Oriented Architecture principle.

## Complexity Tracking

*No violations identified.*
