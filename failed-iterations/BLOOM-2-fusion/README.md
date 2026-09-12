# BLOOM-2 swinging-bucket centrifuge

Fusion 360 prototype for Ficoll/PBMC separation using four 15 mL conical tubes.

## Design point

- Tube mid-fluid radius: **150 mm**
- Exact calculated speed for 400 x g: **1544.4 rpm**
- Controller setpoint: **1545 rpm**
- Resulting RCF: **400.3 x g**
- Swing pivot radius: **86 mm**
- Rotor tip radius at speed: **218 mm**
- Minimum steel-pot inside diameter: **466 mm** (includes 15 mm radial clearance)

The four buckets are modeled in the at-speed horizontal position. Each bucket
rotates about an M3 tangential pivot and has a printed tab that contacts the arm
at 90 degrees. The clevis has 0.5 mm nominal side clearance to the 26 mm bucket
envelope. Use low-friction washers and tighten the nylock only enough to remove
axial play without pinching the bucket.

## Files

- `BLOOM-2_centrifuge_parametric.f3d` - Fusion archive with user parameters,
  shared arm/bucket components, named bodies, and the driven radius reference
- `BLOOM-2_centrifuge_assembly.step` - neutral assembly export
- `stl/` - printable parts; filenames state quantities or option
- `views/` - verified Fusion assembly views
- `bom.csv` - printed and purchased bill of materials
- `build_fusion.py` - reproducible Fusion API build script
- `../../../output/pdf/BLOOM-2_centrifuge_assembly_drawing.pdf` - assembly drawing,
  dimensions, BOM, print notes, and validation plan

## Print setup

- Material: PETG only; dry filament before printing.
- Chassis, hub, and arm: print flat as exported, 0.2 mm layers, 6 perimeters,
  8 top/bottom layers, 70-100% infill. Use 100% around bolt and pivot zones.
- Bucket: print on its side as exported so the principal tensile load runs in
  the layer plane. Use supports under the pivot lug and bore; 6 perimeters and
  100% infill at the lug/stop.
- Print all four arms in one job and all four buckets in one job with identical
  slicer settings. Deburr without removing asymmetric amounts of material.
- Match printed buckets to **+/-0.5 g**. Match opposing loaded tubes to
  **+/-0.1 g** before every run.

## Assembly

1. Press two 608ZZ bearings into the 22.2 mm chassis seats and preload them on
   the 8 mm shaft without side-loading either bearing.
2. Bolt four identical arms to the hub using two M3 fasteners per arm.
3. Install each bucket with an M3x45 pivot, two low-friction washers, and a
   nylock nut. Verify every empty bucket falls freely from vertical to the same
   hard stop by gravity alone.
4. Fit either the direct-drive plate/coupler or the offset 12T:60T gear plate.
   The same four-hole hub interface accepts either configuration.
5. Mount the IR sensor on the tall boss with a 4-8 mm gap to the underside
   target. Mount the MPU-6050 rigidly on the two-hole chassis boss.
6. Install the assembly inside a lidded steel pot with at least 466 mm clear ID.

## Drivetrain notes

Start with direct drive only if the A2212/30 A sensorless ESC starts the fully
loaded rotor smoothly and holds 1545 rpm without desynchronization. Configure a
smooth throttle ramp and coast-only stop; disable active braking. If direct
drive stutters, use the 12T:60T 5:1 option. The included gear STLs are mounting
and fit prototypes with simplified teeth; regenerate/verify true module-1
involute profiles before sustained running.

## Validation gate

This is an engineering prototype, not a certified medical device. Do not begin
with blood. First verify fastener retention, free/equal swing, empty balance,
loaded balance, sensor shutdown, containment, and a guarded overspeed test.
Then run four mass-matched tubes with dyed water over glycerol for 30 minutes at
1545 rpm and coast for more than two minutes. A clean interface is the pass
condition; a smeared or absent interface is a fail.

Made by Codex GPT 5.6 Sol High
