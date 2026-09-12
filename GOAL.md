# PicoCentrifuge

PROBLEM STATEMENT:

The Bloom wet lab loop needs PBMC out of whole blood. That needs a centrifuge holding
400 x g for 30 minutes with a slow coast. Used lab centrifuges run $800 to $3000.
I already own the motor, the ESC, the Pico and a printer.

WHAT I AM BUILDING:

A 3D printed centrifuge. Brushless motor sitting in the base housing, 5x8 coupler up to
an 8 mm rod, bearings in a holder, four-arm rotor on top. Speed held closed loop by a
Raspberry Pi Pico reading an IR tach. MPU-6050 on the chassis for imbalance shutdown.
Runs inside a lidded containment vessel.

CAD OF RECORD:

Onshape, document "ComfyBloom", workspace Main, assembly tab "Centrifuge Assembly".
458 instances. Tabs: Centrifuge, Components, Base, 5X8_COUPLER, Centrifuge Assembly.

URL: [***]

This is the only live design. Everything in failed-iterations/ is dead, do not pull
numbers out of it.

DESIGN POINT:

The requirement is 400 x g at the tube mid-fluid line, held 30 minutes, coast over
2 minutes. RPM falls out of whatever the real rotor radius is:

    rpm = sqrt( RCF / (1.118e-5 * r_cm) )

- Tube mid-fluid radius: [***] measure it off the Onshape assembly
- Setpoint rpm: [***] compute from the above, then round to the controller step
- Material: PETG only, dried

Do not carry the 150 mm / 1545 rpm numbers forward. Those belong to a dead design.

OUTCOME:

A clean Ficoll interface on a dyed-water-over-glycerol run at the setpoint for 30 min.
Smeared or absent interface is a fail. That is the only pass condition that matters.

FRIDAY CONTRACT:

- QUESTION: can a printed rotor on the A2212 hold the setpoint loaded and balanced for 30 min?
- DEADLINE: [***] must be external. grant deadline, a call with a lab, or a date I say
  out loud to Javi at standup. a date I set for myself is an intention, not a deadline.
- ARTIFACT: posts/ writeup, published whether it works or not
- FEEDS: bloom wetlab loop, maker press (SERVO / Hackaday), O-1A original contribution
- KILL DATE: [***]
- BLOCKED-ON-SHIPMENT is a valid state, it is not a stall

VALIDATION GATE:

No blood until all of these pass, in order:

1. fastener retention after 10 min unloaded
2. rotor runs true, no visible wobble at setpoint
3. empty balance, then loaded balance at +/-0.1 g on opposing tubes
4. MPU-6050 shutdown triggers on a deliberate imbalance
5. guarded overspeed test with the lid closed
6. dyed water over glycerol, setpoint, 30 min, coast over 2 min

Engineering prototype, not a certified device. Lid closed for every powered test.

OPEN DESIGN QUESTIONS:

- The assembly has modeled bearings (INNER RACE, OUTER RACE, RETAINER, 8 balls). Are
  those getting printed, or are they a fit model for a real 608 / 8 mm bearing? Printed
  races at 1500+ rpm under a loaded rotor is the thing I would not risk.
- Containment vessel: what is it and what is the clear ID. This killed the last design.
- Rotor is fixed-angle in the render, not swinging. Confirm that is intentional; it
  changes the interface quality on a Ficoll gradient.

NOTES FOR AI AGENTS:

- BOM.md is the source of truth for parts, not the CAD. Reconcile, do not generate.
- Do not write into this file unless I ask, or unless filling a [***].
