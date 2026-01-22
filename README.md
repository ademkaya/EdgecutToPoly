# EdgeToPoly_v2.py - Code Documentation

## 📖 Overview

**EdgeToPoly_v2.py** is a Python utility that automates the conversion of PCB edge outlines (Edge.Cuts layer) in KiCAD PCB files into polygon zones. This is useful when you need to merge complex edge geometries into a single polygon object for various PCB design operations.

### Key Features
- ✅ Automatically detects Edge.Cuts layer segments
- ✅ Orders disconnected segments into a continuous polygon
- ✅ Handles both straight lines and arc segments
- ✅ Creates proper KiCAD ZONE entities
- ✅ Command-line and programmatic usage
- ✅ Comprehensive error handling

---

## 📦 Dependencies

```python
import sys              # System operations
import argparse         # Command-line argument parsing
from pathlib import Path  # File path handling
from kiutils.board import Board  # KiCAD file parsing
import os              # OS operations
import uuid            # UUID generation for zones
```

**External Package Required:**
- `kiutils` - For reading/writing KiCAD PCB files
  ```bash
  pip install kiutils
  ```



## ⚡ Quick Start Examples

### Example 1: Basic Command Line Usage

**Scenario:** You have a KiCAD board `myboard.kicad_pcb` with an Edge.Cuts outline and want to convert it to a polygon zone.

```bash
# Basic - Auto-generates output filename
python EdgeToPoly_v2.py myboard.kicad_pcb

# Output: myboard_edited.kicad_pcb
```

**That's it!** ✨ Your zone has been created.

---

### Example 2: Specify Output File

**Scenario:** You want to keep the original file and save the result with a specific name.

```bash
python EdgeToPoly_v2.py myboard.kicad_pcb -o myboard_with_zone.kicad_pcb
```



---

## 🏗️ Architecture Overview

```
EdgeToPoly_v2.py
│
├── Helper Functions (region)
│   ├── validate_file()
│   ├── order_segments_to_polygon()
│   └── polygon_formatted_output()
│
├── Main Functions (region)
│   ├── create_kicad_zone_entity()
│   ├── append_polygon_to_file()
│   └── process_edge_to_poly()
│
└── CLI Interface
    ├── main()
    └── argparse setup
```
