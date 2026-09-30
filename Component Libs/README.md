# YX55069BCT2 portable KiCad library

`YX55069BCT2.kicad_sym` and `YX55069BCT2.pretty` are self-contained
project libraries. The project tables in `../Kicad Project/` address them by a
project-relative path, so a clone needs neither the Slate113 checkout nor global
KiCad libraries.

The exact requested parts carry their MPN, manufacturer, LCSC part number,
datasheet, and local footprint as symbol properties. `manifest.json` records
the source library and source hash. `tools/build_library.py` reproduces the
library from those sources; normal project use does not run it.

Matching STEP models are stored in `YX55069BCT2.3dshapes` with project-relative
paths. After regenerating the footprint library, run `tools/assign_3d_models.py`
to restore the 3D links in both the library and PCB. The TC358870 BGA STEP came
from EasyEDA/LCSC C3008712, the USB-C STEP from Slate113, and the remaining
models from recorded vendor imports or matching KiCad standard packages.

- `ESP32-S3-WROOM-1-N16R8` uses the PCB-antenna WROOM-1 land pattern. GPIO35,
  GPIO36, and GPIO37 are marked `RESERVED_PSRAM` because N16R8 uses octal
  PSRAM.
- `TC358870XBG(NOK)` is C3008712. Its 1.1 V core/HDMI rails, 1.2 V MIPI D-PHY
  rails, 1.8 V I/O, and 3.3 V I/O/HDMI rails must remain separate.
- `AP2112K-1.2TRG1` was added for the TC358870 1.2 V rail. The requested
  1.8 V and 3.3 V AP2112s and 2.8 V AP2120 remain available.
- The bridge needs an I2C host to set its registers, EDID SRAM and panel
  parameters; it is not a generic plug-and-play MIPI-panel adapter.

See [SOURCING_AND_ARCHITECTURE.md](SOURCING_AND_ARCHITECTURE.md) for sourcing
status and the schematic integration constraints.
