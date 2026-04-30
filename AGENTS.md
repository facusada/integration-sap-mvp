# AI Agent Working Agreement

This repository follows the corporate AI-first workflow:

1. Start every feature with SDD in `docs/sdd/wip/<feature>/spec.md`.
2. Define the TDD plan before implementation.
3. Implement Red -> Green -> Refactor with pytest.
4. Do not connect to real SAP systems unless explicitly approved.
5. Do not hardcode or commit credentials.
6. Keep PyRFC access isolated behind `app/services/sap_rfc_client.py`.
7. Document architectural decisions in `docs/architecture/` when they affect cross-cutting behavior.

Commit convention:

- `feature(module): clear description`
- `fix(module): clear description`

