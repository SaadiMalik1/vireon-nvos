### Acceptance Criteria Checklist
- [x] Laplacian requires `channel_positions`.
- [x] Laplacian output is `data[i] - mean(neighbors)`.
- [x] REST requires `leadfield`.
- [x] REST output is a re-projection.
- [x] Neither returns scalar multiplied mock data.
- [x] NaN raises.
- [x] No `np.random` used.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `spatial.py`.
