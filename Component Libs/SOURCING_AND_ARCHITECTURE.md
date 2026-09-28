# Display bridge sourcing and board architecture

Stock was checked on global LCSC product/catalog pages and DigiKey on
2026-09-24. Search-card availability was not used as evidence.

## Exact board components

This board is HDMI input -> TC358870 -> MIPI DSI panel, with a separate USB-C
USB 2.0 cable for touch. It is not a USB-C DisplayPort Alt Mode display input.
The USB-C connector is therefore only the ESP32 USB device path: D+/D-, ESD,
and two separate 5.1 kohm CC pull-downs. It must not connect to the bridge's
HDMI receiver or DSI output.

| Function | Exact fitted component | LCSC | Documentation |
| --- | --- | --- | --- |
| HDMI input | Amphenol 10029449-001RLF | [C428493](https://www.lcsc.com/product-detail/C428493.html) | [drawing](https://cdn.amphenol-icc.com/media/wysiwyg/files/drawing/10029449.pdf) |
| HDMI to DSI | Toshiba TC358870XBG(NOK) | [C3008712](https://www.lcsc.com/product-detail/C3008712.html) | [datasheet](https://toshiba.semicon-storage.com/info/TC358870XBG_datasheet_en_20171025.pdf?did=28743&prodName=TC358870XBG) |
| Touch HID MCU | ESP32-S3-WROOM-1-N16R8 | [C2913202](https://www.lcsc.com/product-detail/C2913202.html) | [Espressif](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) |
| USB-C USB 2.0 | Shou Han TYPE-C16PIN | [C393939](https://www.lcsc.com/product-detail/C393939.html) | — |
| Optional USB-C PD sink | STMicroelectronics STUSB4500QTR | [C2678061](https://www.lcsc.com/product-detail/C2678061.html) | [ST datasheet](https://www.st.com/resource/en/datasheet/stusb4500.pdf) |
| Display FPC | CKMTW F-FPC0M24P-C310 | [C132514](https://www.lcsc.com/product-detail/C132514.html) | — |
| Touch FPC | Xunpu FPC-0.5FX-6PWBH10 | [C5343255](https://www.lcsc.com/product-detail/C5343255.html) | — |
| I2C translation | TI PCA9306DCUR | [C33196](https://www.lcsc.com/product-detail/C33196.html) | [TI](https://www.ti.com/product/PCA9306) |
| USB ESD | ST USBLC6-2SC6 | [C7519](https://www.lcsc.com/product-detail/C7519.html) | [ST](https://www.st.com/resource/en/datasheet/usblc6-2.pdf) |
| 3.3 V LDO | Diodes AP2112K-3.3TRG1 | [C51118](https://www.lcsc.com/product-detail/C51118.html) | [Diodes](https://www.diodes.com/part/view/AP2112) |
| Optional 3.3 V LDO | Seaward Elec SED5120 | [C2838439](https://www.lcsc.com/product-detail/C2838439.html) | [datasheet](https://lcsc.com/datasheet/lcsc_datasheet_2410121612_Seaward-Elec-SED5120_C2838439.pdf) |
| 1.8 V LDO | Diodes AP2112K-1.8TRG1 | [C176944](https://www.lcsc.com/product-detail/C176944.html) | [Diodes](https://www.diodes.com/part/view/AP2112) |
| 2.8 V LDO | Diodes AP2120N-2.8TRG1 | [C6500826](https://www.lcsc.com/product-detail/C6500826.html) | [Diodes](https://www.diodes.com/datasheet/download/AP2120.pdf) |
| 1.2 V LDO | Diodes AP2112K-1.2TRG1 | [C460310](https://www.lcsc.com/product-detail/C460310.html) | [Diodes](https://www.diodes.com/part/view/AP2112) |
| Backlight candidate | TI LP8556SQ-E09/NOPB | [C2679180](https://www.lcsc.com/product-image/C2679180.html) | [TI](https://www.ti.com/lit/ds/symlink/lp8556.pdf) |

The global LCSC product page showed **187** TC358870XBG(NOK) available to ship.
It is HDMI 1.4b RX to MIPI DSI 1.1 TX: 297 MHz HDMI maximum, one four-lane DSI
link at up to 1 Gbit/s/lane, or two four-lane links. The documented single-link
limits are 2558 pixels wide at 24 bpp and 3411 at 16 bpp. It has no scaler or
deinterlacer. With no panel model, resolution, lane count, DCS sequence,
refresh range, backlight string, or FPC pinout, compatibility remains unknown.

TC358870 is **register-configured, not proprietary-firmware booted**. A host
sets its I2C registers, EDID SRAM, and panel control; there is no required
vendor SPI image. Public third-party source exists at
[CNflysky/TC358870](https://github.com/CNflysky/TC358870), but it is not a
manufacturer-supported universal panel binary.

## USB-C DisplayPort Alt Mode -> MIPI DSI

No current global-LCSC or DigiKey part was verified that meets all of: USB-C DP
Alt Mode input, MIPI DSI output, open/publicly sufficient implementation, and
no proprietary vendor firmware.

| Candidate | Direction/capability | Firmware class | Constraint that fails |
| --- | --- | --- | --- |
| LT7911D / C5310990 | Type-C/DP1.2 to MIPI DSI/CSI/LVDS, 1.5 Gbit/s/lane | Factory embedded MCU; confidential documentation | Global LCSC direct route reports part not found. |
| LT7911UXC / C5310989 | Type-C/DP1.4 to MIPI/CSI/LVDS | Factory embedded MCU and SPI-flash firmware | Global LCSC says **Not available now**. |
| Analogix ANX7530/ANX7580 | DP to dual/single MIPI DSI | Public non-proprietary implementation not established | Manufacturer capability exists, but no global LCSC/DigiKey stock was verified. [Analogix](https://www.analogix.com/en/mipi/converters/bridges) |
| TC358870XBG | **HDMI** to DSI | Register-configured | In stock, but wrong input direction for this search. |

Any discrete DP-to-DSI implementation still needs Type-C CC/PD policy,
orientation/lane mapping and normally a high-speed mux. Four DP lanes consume
the SuperSpeed pairs; USB 3.x coexistence means two-lane DP and less bandwidth.
This board needs none of that because its video and touch cables are separate.

## USB-C DP Alt Mode -> HDMI versus MCDP5200B0T

`MCDP5200B0T` was live at DigiKey with **445 pieces**: MPN `MCDP5200B0T`,
orderable as `2763-MCDP5200B0TCT-ND` cut tape,
`2763-MCDP5200B0TTR-ND` reel, or `2763-MCDP5200B0TDKR-ND` Digi-Reel.
[DigiKey listing](https://www.digikey.com/en/products/detail/kinetic-technologies/MCDP5200B0T/13557894).
It has DP1.4a Alt Mode, HDMI 2.0b, HBR3, up to 4K60 RGB/YCC444 or 4K120 YCC420,
and USB3.1 demux. It fails the request because secure boot authenticates a
signed application image from external 16-Mbit SPI flash:
[datasheet brief](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6727/MCDP5200B0T%20Datasheet.pdf).

No currently in-stock functional alternative without proprietary vendor
firmware was verified.

| Candidate | What it replaces | Firmware class | Constraint that fails |
| --- | --- | --- | --- |
| Parade PS176 / C209703 | DP/DP Alt Mode to HDMI 2.0, 4K60 | Factory internal SPI ROM/microcode | Global LCSC says **Not available now**; no open firmware. [Parade](https://www.paradetech.com/products/ps176/) |
| Lontium LT8711GX / C5310994 | Type-C/DP1.4a to HDMI2.1 with CC/PD | Embedded MCU and SPI flash for firmware/HDCP keys | Global LCSC says **Not available now** and the firmware is closed. [LCSC](https://www.lcsc.com/product-detail/C5310994.html) |
| Kinetic STDP2690ADT | Native DP to DP++/HDMI-class output | Internal ROM plus optional external custom flash | DigiKey reports **0 stock** and discontinued. It is HDMI 1.2a/DP++ class and lacks MCDP5200's integrated Type-C/USB3.1 demux. [DigiKey](https://www.digikey.com/en/products/detail/kinetic-technologies/STDP2690ADT/15976326) |

## Schematic integration checklist

- Use controlled-impedance, length-matched HDMI TMDS and MIPI DSI pairs. Route
  DDC, HPD and CEC exactly per the bridge reference material.
- TC358870 needs 1.1 V core/HDMI rails, separate 1.2 V MIPI rails, 1.8 V I/O,
  3.3 V HDMI/I/O rails, local decoupling, 2 kohm REXT, 40-50 MHz 1.8 V REFCLK,
  RESETN, I2C, and accessible test/programming pads.
- SED5120 is an optional nominal 3.3 V regulator, not a drop-in guarantee for
  AP2112K-3.3: calculate worst-case SOT-223 dissipation from the selected input
  voltage and load, and use the output capacitance specified by its datasheet.
- Map the display FPC only after obtaining its panel drawing. Connector pin
  count does not prove MIPI pinout or video-mode compatibility.
- PCA9306 translates open-drain I2C only. Use the lower rail on VREF1,
  VREF2/EN through 200 kohm to the high rail, and pull-ups on both sides.
  Translate any push-pull touch reset/interrupt signal separately.
- If STUSB4500QTR is fitted on the USB-C touch/power port, its CC pins own
  attachment and PD-sink negotiation. Do not also fit the two discrete 5.1
  kohm CC pull-downs. It does not add DisplayPort Alt Mode capability.
- GT911 requirements still need the actual panel drawing. Confirm VDDIO,
  INT/RST boot levels, address selection, and whether 2.8 V is correct.
- CircuitPython supports custom `usb_hid.Device` descriptors, so ESP32-S3 can
  expose a HID digitizer. Stock mouse HID is not a multi-touch digitizer.
  [CircuitPython API](https://docs.circuitpython.org/en/stable/shared-bindings/usb_hid/)
- LP8556 is a six-channel boost driver. Inductor, diode, output capacitors,
  current setting and string count are intentionally marked TBD until the
  panel backlight data is known.
