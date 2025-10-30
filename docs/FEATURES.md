# Engineered Feature Catalog

| Feature | Formula | Business Insight | Example Use |
| --- | --- | --- | --- |
| `complexity_per_cm3` | `path_length_mm / volume_removed_cm3` | Normalizes CAM path complexity by material removed to compare sculpt designs. | Flag toolpaths likely to require slower feeds or additional finishing passes. |
| `load_per_mm` | `spindle_current_a / path_length_mm` | Indicates electrical load per millimeter of motion, highlighting stress on tooling. | Predict preventative maintenance windows for spindles and cutters. |
| `energy_per_cm3` | `energy_kwh / volume_removed_cm3` | Measures energy efficiency per unit material removed. | Optimize stone assignment to shifts or machines with lower energy budgets. |
| `tool_efficiency` | `volume_removed_cm3 / tool_wear_cost_usd` | Shows how far each tool dollar stretches for material removal. | Rank tool libraries, justify regrind cycles, and negotiate supplier terms. |
| `profit_margin` | `(revenue_usd - tool_wear_cost_usd) / revenue_usd` | Captures contribution margin per job before fixed overhead. | Focus account management on designs and stones with healthy margins. |
| `quality_vs_speed` | `surface_score / (duration_s / 60)` | Balances finish quality against cycle time to expose trade-offs. | Tune feed overrides or CAM strategies for better finish within SLA. |
