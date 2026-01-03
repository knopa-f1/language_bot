Context:
This is a Python Telegram bot project deployed via Docker.
The project currently uses a requirements file for dependency management.
A requirements file with dependencies is already present in the repository.

Your task is to migrate the project to Poetry for dependency management
and update documentation accordingly.

This task must be done carefully and in a controlled manner.

Hard constraints (must follow strictly):
- Work only inside this repository
- Do NOT change application logic unless strictly required
- Do NOT upgrade dependency versions unless necessary for Poetry compatibility
- Preserve Python version compatibility
- Do NOT introduce alternative tools (pipenv, uv, etc.)
- Keep changes minimal and well scoped

Migration goals:

1) Dependency management (Poetry)
   - Create pyproject.toml configured for Poetry
   - Migrate dependencies from the existing requirements file
   - Separate main and dev dependencies if applicable
   - Generate poetry.lock
   - Keep dependency versions aligned with the current setup

2) README.md (usage with Poetry)
   Update README.md ONLY to document how to USE this project with Poetry
   when working directly with this repository.

   README.md must include:
   - How to install Poetry
   - How to install project dependencies using Poetry
   - How to run the project locally using Poetry

   README.md must NOT include:
   - Migration rationale
   - Explanations of why Poetry was chosen
   - Instructions for converting from requirements

   Treat README.md as end-user / contributor documentation.

3) MIGRATION.md (migration guide)
   - Create a new MIGRATION.md file
   - This file must explain:
     - Why the project moved from requirements to Poetry
     - How to migrate an existing local environment
       from requirements.txt to Poetry
     - Mapping of old pip-based commands to Poetry commands
   - This file is for developers only and must be separate from README.md

4) Docker integration
   - Update Dockerfile to install dependencies using Poetry
   - Use Poetry in a way suitable for Docker (no nested virtualenvs)
   - Ensure Docker build remains reproducible
   - Do NOT change runtime behavior of the application

Implementation requirements:
- Follow Poetry best practices
- Avoid unnecessary complexity in Dockerfile
- Keep Docker image size reasonable
- Follow existing project conventions and style

Completion requirements:
- Modify only files related to:
  dependency management, documentation, and Docker
- Do NOT touch monitoring, Grafana dashboards, or application logic
- Summarize all changed and added files
- Do NOT suggest additional refactors or improvements beyond this migration
