# Log

Newest first. Voice notes go in logs/ and get transcribed. Photos go in photos/, dated,
no captions needed.

## 2026-09-11 - moved to Onshape, BLOOM-2 retired

Rebuilt the whole thing in Onshape. Document "ComfyBloom", assembly "Centrifuge Assembly",
458 instances. Different architecture: motor sits in the base housing with the ESC, 5x8
coupler up to an 8 mm rod, bearings in a holder, four-arm rotor on top. M4 hardware.

BLOOM-2 and the loose STLs moved to failed-iterations/. Nothing gets pulled out of there.

## 2026-08-09 - BLOOM-2 finished on paper, never built

Agent-generated swinging-bucket design in Fusion off a Jira ticket. Complete package:
parametric file, STEP, nine STLs, assembly drawing, BOM, build script. Needed a 466 mm
clear ID containment vessel. Dead.

## 2026-08-08 - A2212 ramp test on Pico

Motor and ESC ran clean off a MicroPython ramp script. No load, no rotor. Confirmed the
drivetrain is not the hard part.

## 2026-08-08 - decided to build rather than buy

Used lab centrifuges run $800 to $3000. I already own the motor, ESC, Pico and printer.
Stripped it to the physical function: hold 400 x g for 30 minutes with a slow coast and
do not throw a tube. That is a motor, a balanced rotor, a speed loop and a lid.

## Open blockers

1. blood sample and tumor sample
2. containment vessel, clear ID still unknown
