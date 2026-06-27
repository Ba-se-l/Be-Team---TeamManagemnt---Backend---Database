"""Deprecated file.

Dependency injection logic specifically tied to domain models (like `get_current_user`)
has been moved to `src.modules.auth.dependencies` to prevent Topological Circular Imports.

Do not add new dependencies here unless they are completely agnostic to the `src.modules` domain.
"""