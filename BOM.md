# BOM

Source of truth for parts. Not generated from CAD. Friday reconciles this against the
Onshape assembly and tells me what is unaccounted for.

Status: `have` / `ordered` / `need` / `failed`

## Owned

| Item | Qty | Spec | Status | Notes |
|---|---|---|---|---|
| A2212 brushless motor | 1 | 1000 KV, 5 mm shaft | have | ramp tested on Pico, ran clean |
| Sensorless ESC | 1 | 30 A | have | brake disabled, smooth ramp programmed |
| Raspberry Pi Pico | 1 | MicroPython | have | running the ramp script |
| 2S LiPo | 1 | ~7.4 V | have | needs a fuse and a physical disconnect |
| Printer | 1 | Bambu A1 mini | have | PETG, dry the filament |

## Need

| Item | Qty | Spec | Status | Notes |
|---|---|---|---|---|
| 8 mm rod | 1 | ~100-125 mm | need | ground steel preferred |
| Coupler 5 to 8 mm | 1 | rigid | need | modeled as tab 5X8_COUPLER. buy it, do not print it |
| Bearing | 2 | [***] confirm size | need | see open question below |
| M4 x 6 screw | [***] | - | need | assembly uses M4x6-Vis throughout |
| IR reflective sensor | 1 | optical tachometer | need | 4-8 mm gap to an underside target |
| MPU-6050 | 1 | - | need | mount flat and rigid near the bearing holder. NOT next to the rotor |
| 15 mL conical tube | 4 | 17 x 120 mm | need | opposing tubes matched to +/-0.1 g |
| Containment vessel + lid | 1 | clear ID [***] | need | measure rotor tip radius first |
| Glycerol + dye | 1 | - | need | validation run, before any blood |

## Printed

PETG, dried. Print matched sets in one job with identical slicer settings.

| Part | Qty | Onshape name | Notes |
|---|---|---|---|
| Base | 1 | Base | houses motor and ESC |
| Base Cover | 1 | Base Cover | - |
| Bearing Holder | 1 | Bearing Holder | - |
| Top | 1 | Top | - |
| Rotor | 1 | Rotor | four arm cross. mass match arms |
| Corps | 2 | Corps | [***] what is this, label it |
| Cover / races / retainer | - | COVER, INNER RACE, OUTER RACE, RETAINER | see open question |

## Open questions

- **Bearings.** The assembly models a full bearing: INNER RACE, OUTER RACE, RETAINER and
  8 balls. Is that getting printed or is it a fit model for a bought bearing? Printed
  races carrying a loaded rotor at 1500+ rpm is the one thing I would not risk. If it is
  a fit model, put the real part number here and delete this line.
- **Rotor angle.** Render looks fixed-angle, not swinging. Fixed-angle works for Ficoll
  but gives a slanted interface and a harder draw. Confirm it is intentional.
- **Containment vessel.** Already modeled as `Pot` in the Base studio, rotor sits inside
  it. Confirm the real-world part it is modeled from and put it in the Need table above.
  Sourcing this is what killed BLOOM-2.
- **Unnamed parts.** Base studio still has `Part 8`, `Part 9`, `Part 10`, `Part 11` and
  `fit tes`. Render filenames come from part names, so these read badly in a build log.
