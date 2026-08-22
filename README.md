# VergeGPT - Unrestricted AI Assistant

## Overview

VergeGPT is an open-source development assistant interface that routes queries to external language model APIs. It features an integrated local file management and protection framework to maintain user workspace safety during script testing and execution.

---

## User Interface

Below is an overview of the application layout, configuration modules, and operational views of the workspace environment.

### Main Interface Dashboard

<img src="https://github.com/user-attachments/assets/0c14730a-feca-4d62-8f51-b185bb46e5cd" width="500">
---

## System Features

### Interface and Routing
*   **Provider Integration:** Configurable endpoints for API routing via OpenRouter, DeepSeek, and OpenAI.
*   **User Interface:** Modern glassmorphism interface equipped with native theme selections.
*   **Session Management:** Local retention architecture for saving, viewing, and loading historical chat timelines.
*   **Code Execution Environment:** Integrated tools to run local scripts directly from the utility interface.
*   **Template Library:** Built-in repository for managing and deploying reusable code snippets.

### File Protection System
The local execution sandbox enforces a strict state-preservation protocol:
*   **Automated State Capture:** Automatic background generation of point-in-time file backups.
*   **Privilege Restriction:** System-level blocks preventing automated removal of user-created entities.
*   **State Restoration:** Rollback recovery systems to restore missing or modified assets from stored backups.
*   **Explicit Consent Verification:** Strict interactive authorization required for any high-risk directory actions.
*   **Transactional Ledger:** Comprehensive audit logs logging all workspace file modifications.

---

## Deployment and Setup

### Prerequisites
*   Python 3.8 or higher
*   Valid API credentials for selected upstream providers

### Target Installation
```bash
git clone https://github.com
cd vergegpt
pip install -e .
```

### Application Initialization

#### Command-Line Interface
```bash
vergegpt
```

#### Graphical Interface
```bash
vergegpt-gui
```

---

## Configuration

Environment variables must be specified via a local configuration file. Construct a `.env` file within the root project folder using the following format:

```ini
VERGEGPT_API_KEY=your_api_key_here
VERGEGPT_API_PROVIDER=openrouter
```

Configuration variables can also be managed directly using the settings dialog inside the graphical user interface.

---

---

## Operational Notice and Disclaimer

This software serves strictly as an agnostic interface layer executing tasks down to third-party endpoints. It is provided "as-is," and this software may or may not work depending on upstream API stability, environment configurations, or third-party modifications. It lacks built-in administrative guardrails or classification logic.

Users accept all legal and operational obligations regarding the generation, testing, and deployment of security evaluation materials, network diagnostics, or automated scripts. Configuration and deployment should be limited entirely to sandboxed research environments and infrastructure owned explicitly by the operator.
