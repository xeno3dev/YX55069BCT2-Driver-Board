![PCB Render](https://cdn.hackclub.com/01a0fd6a-23ed-787f-be4e-52df6e712e9c/journal-1790957986161.png)

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-blue.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

# LumaDD

## Overview

LumaDD is a Custom Display Driver Board designed around a display I got off [Alibaba](https://www.alibaba.com/product-detail/5-5-Vertical-Smart-Home-lcd_1601790231031.html?spm=a2756.trade-list-buyer.0.0.36a276e9iccSGK), with Touch Support. It features HDMI -> MIPI DSI video signal conversion, USB-C for Touch Signals + Power, as well as an onboard ESP32-S3 for display control + touch processing (via USB HID)

## Repo Directory

Folder | Contents
|---|---|
Component Libs | All 3D Models. Footprints, and Symbols used on the PCB
Kicad Project | Schematic + PCB Files
Production Files | BOM + CPL + Netlist + Designator + Gerber Files

## Rough BOM
| Part / Group | What’s included | Qty | Cost (USD) |
| --- | --- | ---: | ---: |
| Converter BGA | [TC358870XBG](https://www.lcsc.com/product-detail/C3008712.html), U1 | 1 | $8.86 |
| ESP32 by itself | [ESP32-S3R8](https://www.lcsc.com/product-detail/C2913194.html), U10 | 1 | $3.02 |
| Flash memory | [GD25Q128EWIGR](https://www.lcsc.com/product-detail/C2982923.html), U11 | 1 | $3.33 |
| HDMI port | [Amphenol 10029449-111RLF](https://www.lcsc.com/product-detail/C427307.html) | 1 | $0.62 |
| USB-C port | [TYPE-C16PIN](https://www.lcsc.com/product-detail/C393939.html) | 1 | $0.06 |
| Display connector | [24-pin FPC](https://www.lcsc.com/product-detail/C132514.html) | 1 | $0.25 |
| Touch connector | [6-pin FPC](https://www.lcsc.com/product-detail/C5343255.html) | 1 | $0.15 |
| Power regulation and input control | Five TLV767 regulators, CH224K, TPS259474 eFuse | 7 | $3.64 |
| Backlight power stage | TPS61165, inductor, diode | 3 | $1.09 |
| Logic level shifters | Two PCA9306, TXS0101, SN74AXC1T45 | 4 | $2.39 |
| ESD / surge protection | D3–D5, U8, U12, U16 | 6 | $1.46 |
| Clock components | 40 MHz crystal and 48 MHz oscillator | 2 | $1.50 |
| Boot / reset buttons | SW3 and SW4 | 2 | $2.29 |
| Capacitors | All BOM capacitors | 72 | $1.97 |
| Resistors | All BOM resistors | 40 | $0.36 |
| MOSFETs | Three BSS138 | 3 | $0.06 |
| Ferrite beads | FB1 and FB2 | 2 | $0.03 |
| **Total parts used** | **148 components** | **148** | **$31.07** |

### Full BOM Located [Here](./Production%20Files/bom.csv)

## License

[Attribution-NonCommercial-ShareAlike 4.0 International](./LICENSE)