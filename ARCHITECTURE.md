# Architecture Documentation

## Repository Pattern Implementation

### Current Status

The repository interfaces are currently maintained in:
- `backend/common/repositories.py` (current implementation)
- `backend/core/repository_interfaces.py` (future implementation)

### Migration Plan

1. **Phase 1 (Current)**: 
   - All new code should import from `backend.core.repository_interfaces`
   - `core.repository_interfaces` re-exports from `common.repositories`

2. **Phase 2 (Next Release)**:
   - Move all interfaces to `core.repository_interfaces` 
   - Add deprecation warnings to `common.repositories`
   - Update existing imports

3. **Phase 3 (Future Release)**:
   - Remove `common.repositories`
   - All code should import directly from `core.repository_interfaces`

### Rationale

This phased approach allows gradual migration without breaking changes, while moving toward a cleaner architecture that places core interfaces in the `core` package.
