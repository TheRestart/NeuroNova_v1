# NeuroNova Project Structure & Documentation Guide

This document serves as a unified guide to the project structure, merging the descriptions of individual directories and listing key documentation.

## Project Directory Structure

### 📂 Root Directory
- **README.md**: The main entry point for the project. Contains high-level overview, quick start guide, and team info.
- **start_project.bat / .ps1**: Scripts to launch the development environment (backend + frontend).

### 📂 00_UML
- **Description**: Contains Unified Modeling Language (UML) diagrams and design artifacts.
- **Contents**:
  - StarUML files (`.mdj`)
  - Exported diagrams (Sequence, Class, ERD)
  - Use Case definitions

### 📂 01_doc
- **Description**: The central library for all project documentation.
- **Key Documents**:
  - `CLAUDE_CONTEXT.md`: Context file for AI onboarding.
  - `업무계획서.md`: Detailed business logic and project plan.
  - `03_개발_작업_순서.md`: Step-by-step development roadmap.
  - `08_API_명세서.md`: API endpoints and specifications.
  - `09_데이터베이스_스키마.md`: Database schema definitions.
  - `11_배포_가이드.md`: Production deployment guide.

### 📂 02_back_end
- **Description**: Backend Server Application.
- **Tech Stack**: Django REST Framework, Python.
- **Key Subdirectories**:
  - `01_django_server/`: The main Django project root.
  - `02_openemr_server/`: OpenEMR integration configurations.

### 📂 03_front_end_react
- **Description**: Web Frontend Application for Medical Staff.
- **Tech Stack**: React, TypeScript, Tailwind CSS, Zustand.
- **Target Users**: Doctor, Nurse, Admin, RIB, Lab, External.
- **Key Subdirectories**:
  - `01_react_client/`: The React source code.

### 📂 04_front_end_flutter
- **Description**: Mobile Frontend Application for Patients.
- **Tech Stack**: Flutter (Dart).
- **Target Users**: Patients (Appointment booking, Medical history).

---

## Documentation Integration Strategy

This project uses a hybrid approach:
1. **Root README.md**: High-level overview and index.
2. **Directory READMEs**: Context-specific information located where the code lives (good for GitHub browsing).
3. **01_doc/**: Detailed consolidated documentation for deep dives.

This file (`PROJECT_STRUCTURE.md`) acts as an integrated map of the folder system.
