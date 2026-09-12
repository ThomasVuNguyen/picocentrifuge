"""Build the BLOOM-2 swinging-bucket centrifuge in Autodesk Fusion.

Run inside Fusion through the installed Fusion360MCP `execute_code` command.
All numeric geometry is expressed in Fusion internal centimetres.  The model
contains named user parameters and a radius reference sketch so the selected
150 mm mid-fluid radius and derived 1545 rpm remain explicit in the archive.
"""

import adsk.core
import adsk.fusion
import math
import os


OUT_DIR = "/Users/thomasthemaker/Development/ComfySpace/comfybloom/2-wetlab/hardware/centrifuge"
STL_DIR = os.path.join(OUT_DIR, "stl")
VIEW_DIR = os.path.join(OUT_DIR, "views")

# Ticket-driven dimensions (millimetres unless stated otherwise).
ROTOR_RADIUS = 150.0       # tube mid-fluid radius
BUCKET_MOUTH_OFFSET = 4.0  # pivot axis to tube-pocket entrance
TUBE_LENGTH = 120.0
TUBE_MID_OFFSET = BUCKET_MOUTH_OFFSET + TUBE_LENGTH / 2.0
PIVOT_RADIUS = ROTOR_RADIUS - TUBE_MID_OFFSET
TARGET_RCF = 400.0
CALCULATED_RPM = math.sqrt(TARGET_RCF / (1.118e-5 * (ROTOR_RADIUS / 10.0)))
DESIGN_RPM = 1545.0        # rounded controller setpoint
RESULTING_RCF = 1.118e-5 * (ROTOR_RADIUS / 10.0) * DESIGN_RPM * DESIGN_RPM
HUB_Z = 128.0
ARM_Z = 140.0
PIVOT_Z_LOCAL = 32.0
BUCKET_LENGTH = 128.0
BUCKET_OD = 26.0
BUCKET_ID = 18.6


def cm(mm):
    return mm / 10.0


def p(x, y, z):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def v(x, y, z):
    return adsk.core.Vector3D.create(x, y, z)


def matrix(angle_deg=0.0, tx=0.0, ty=0.0, tz=0.0):
    m = adsk.core.Matrix3D.create()
    if angle_deg:
        m.setToRotation(math.radians(angle_deg), v(0, 0, 1), p(0, 0, 0))
    m.translation = v(cm(tx), cm(ty), cm(tz))
    return m


def add_component(root, name, transform=None):
    occ = root.occurrences.addNewComponent(transform or matrix())
    occ.component.name = name
    return occ, occ.component


def add_body(comp, temp_body, name):
    feat = comp.features.baseFeatures.add()
    feat.startEdit()
    body = comp.bRepBodies.add(temp_body, feat)
    body.name = name
    feat.finishEdit()
    # Fusion can invalidate the object returned while a base feature is being
    # edited. Reacquire it so both naming and later export target the live body.
    body = comp.bRepBodies.item(comp.bRepBodies.count - 1)
    body.name = name
    return body


def cylinder(tm, start, end, radius):
    return tm.createCylinderOrCone(p(*start), cm(radius), p(*end), cm(radius))


def box(tm, center, size, xdir=(1, 0, 0), ydir=(0, 1, 0)):
    obb = adsk.core.OrientedBoundingBox3D.create(
        p(*center), v(*xdir), v(*ydir), cm(size[0]), cm(size[1]), cm(size[2])
    )
    return tm.createBox(obb)


def cut(tm, target, tool):
    ok = tm.booleanOperation(target, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType)
    if not ok:
        raise RuntimeError("Temporary BRep cut failed")
    return target


def join(tm, target, tool):
    ok = tm.booleanOperation(target, tool, adsk.fusion.BooleanTypes.UnionBooleanType)
    if not ok:
        raise RuntimeError("Temporary BRep union failed")
    return target


def ring(tm, z0, z1, ro, ri):
    body = cylinder(tm, (0, 0, z0), (0, 0, z1), ro)
    return cut(tm, body, cylinder(tm, (0, 0, z0 - 1), (0, 0, z1 + 1), ri))


def drill_z(tm, body, x, y, z0, z1, radius=1.7):
    return cut(tm, body, cylinder(tm, (x, y, z0), (x, y, z1), radius))


def add_parameters(design):
    params = design.userParameters
    for i in range(params.count - 1, -1, -1):
        try:
            params.item(i).deleteMe()
        except Exception:
            pass

    def add(name, expr, units, note):
        return params.add(name, adsk.core.ValueInput.createByString(expr), units, note)

    add("RotorRadius", "150 mm", "mm", "Driven mid-fluid radius from BLOOM-2")
    add("TubeLength", "120 mm", "mm", "Nominal 15 mL conical tube length")
    add("BucketMouthOffset", "4 mm", "mm", "Pivot axis to tube-pocket entrance")
    add("TubeMidOffset", "BucketMouthOffset + TubeLength / 2", "mm", "Pivot axis to tube mid-fluid point")
    add("PivotRadius", "RotorRadius - TubeMidOffset", "mm", "Swing pivot radius")
    add("BucketLength", "128 mm", "mm", "Holder length for 17 x 120 mm tube")
    add("BucketID", "18.6 mm", "mm", "Clearance bore for 17 mm tube")
    add("TargetRCF", "400", "", "Required relative centrifugal force")
    add("CalculatedRPM", f"{CALCULATED_RPM:.3f}", "", "Exact rpm from sqrt(RCF/(1.118e-5*r_cm))")
    add("DesignRPM", f"{DESIGN_RPM:.0f}", "", "Rounded controller setpoint; update when RotorRadius changes")
    add("ResultingRCF", f"{RESULTING_RCF:.3f}", "", "RCF at DesignRPM and RotorRadius")
    add("MinPotID", "466 mm", "mm", "436 mm rotor envelope plus 15 mm radial clearance per side")


def add_radius_reference(root):
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.name = "PARAMETER_REFERENCE_RotorRadius"
    circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(p(0, 0, 0), cm(ROTOR_RADIUS))
    dim = sketch.sketchDimensions.addDiameterDimension(circle, p(ROTOR_RADIUS + 20, 0, 0))
    dim.parameter.expression = "2 * RotorRadius"
    sketch.isVisible = False


def build_chassis(root, tm):
    occ, comp = add_component(root, "01_CHASSIS")
    # 200 mm ring plus two load paths: printable on a 220 x 220 bed.
    base = ring(tm, 0, 8, 100, 82)
    join(tm, base, box(tm, (0, 0, 4), (200, 24, 8)))
    join(tm, base, box(tm, (0, 0, 4), (24, 200, 8)))

    # Four M3 pot/chassis hold-downs.
    for a in (45, 135, 225, 315):
        x, y = 91 * math.cos(math.radians(a)), 91 * math.sin(math.radians(a))
        drill_z(tm, base, x, y, -1, 9)

    # Dual 608ZZ bearing tower: 22.2 mm seats, 8.3 mm through bore.
    tower = cylinder(tm, (0, 0, 8), (0, 0, 126), 30)
    cut(tm, tower, cylinder(tm, (0, 0, 6), (0, 0, 142), 4.15))
    cut(tm, tower, cylinder(tm, (0, 0, 40), (0, 0, 47.2), 11.1))
    cut(tm, tower, cylinder(tm, (0, 0, 112.8), (0, 0, 120.0), 11.1))
    join(tm, base, tower)

    # Stiffening webs around the bearing tower.
    for a in (0, 90, 180, 270):
        rad, tan = (math.cos(math.radians(a)), math.sin(math.radians(a))), (-math.sin(math.radians(a)), math.cos(math.radians(a)))
        web = box(tm, (22 * rad[0], 22 * rad[1], 42), (44, 8, 68), (rad[0], rad[1], 0), (tan[0], tan[1], 0))
        join(tm, base, web)

    # IR reflective sensor pedestal, aligned to a rotor target at r=45 mm.
    ir = box(tm, (45, 0, 65), (28, 20, 114))
    join(tm, base, ir)
    drill_z(tm, base, 40, 0, 118, 130)
    drill_z(tm, base, 50, 0, 118, 130)

    # Rigid MPU-6050 boss (no isolation), two M3 holes at 20 mm spacing.
    mpu = box(tm, (-68, 0, 11), (30, 24, 6))
    join(tm, base, mpu)
    drill_z(tm, base, -78, 0, 7, 16)
    drill_z(tm, base, -58, 0, 7, 16)

    # Common M3 mounting patterns for direct and 5:1 offset motor plates.
    for cx in (0, 36):
        for dx, dy in ((-8, -9.5), (-8, 9.5), (8, -9.5), (8, 9.5)):
            drill_z(tm, base, cx + dx, dy, -1, 9)

    # Recut these last: the four tower webs intersect the centerline and would
    # otherwise refill part of the shaft bore and lower bearing seat.
    cut(tm, base, cylinder(tm, (0, 0, -1), (0, 0, 142), 4.15))
    cut(tm, base, cylinder(tm, (0, 0, 40), (0, 0, 47.2), 11.1))
    cut(tm, base, cylinder(tm, (0, 0, 112.8), (0, 0, 120.0), 11.1))

    body = add_body(comp, base, "Chassis_BearingTower_SensorBosses")
    return occ, comp, body


def build_hub(root, tm):
    occ, comp = add_component(root, "02_ROTOR_HUB", matrix(tz=HUB_Z))
    hub = cylinder(tm, (0, 0, 0), (0, 0, 12), 35)
    cut(tm, hub, cylinder(tm, (0, 0, -1), (0, 0, 14), 4.1))

    # Four identical arm lands and two M3 fasteners per arm.
    for a in (0, 90, 180, 270):
        rdir = (math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
        tdir = (-math.sin(math.radians(a)), math.cos(math.radians(a)), 0)
        pad = box(tm, (35 * rdir[0], 35 * rdir[1], 6), (22, 28, 12), rdir, tdir)
        join(tm, hub, pad)
        for rr in (30, 40):
            drill_z(tm, hub, rr * rdir[0], rr * rdir[1], -1, 14)

    # Shared direct-coupler / gear-carrier M3 interface, 24 mm BCD.
    for a in (45, 135, 225, 315):
        drill_z(tm, hub, 12 * math.cos(math.radians(a)), 12 * math.sin(math.radians(a)), -1, 20)

    # Underside optical target gives strong reflective/dark contrast at r=45 mm.
    target = box(tm, (45, 0, -1), (22, 12, 2))
    join(tm, hub, target)
    body = add_body(comp, hub, "Rotor_Hub_4Arm_Interface_IR_Target")
    return occ, comp, body


def build_arm(root, tm):
    occ, comp = add_component(root, "03_ROTOR_ARM_MASTER_x4", matrix(tz=ARM_Z))
    # Keep the inner arm solid, then split it into two rails before the pivot.
    # The gap between the rails clears the 26 mm bucket envelope while it hangs
    # vertically at rest; a solid beam under the pivot would intersect the tube.
    fork_start = PIVOT_RADIUS - 20.0
    arm = box(tm, ((25 + fork_start) / 2, 0, 6), (fork_start - 25, 26, 12))
    for y in (-16.0, 16.0):
        rail = box(tm, ((fork_start + PIVOT_RADIUS + 12) / 2, y, 6),
                   (PIVOT_RADIUS + 12 - fork_start, 5, 12))
        join(tm, arm, rail)
    for x in (30, 40):
        drill_z(tm, arm, x, 0, -1, 14)

    # Clevis ears sit outside the bucket's 26 mm OD with 0.5 mm clearance.
    for y in (-16.0, 16.0):
        ear = box(tm, (PIVOT_RADIUS, y, 21), (24, 5, 42))
        join(tm, arm, ear)
    # M3 pivot bore runs tangentially through both ears.
    pivot_hole = cylinder(
        tm,
        (PIVOT_RADIUS, -21, PIVOT_Z_LOCAL),
        (PIVOT_RADIUS, 21, PIVOT_Z_LOCAL),
        1.7,
    )
    cut(tm, arm, pivot_hole)
    body = add_body(comp, arm, "Rotor_Arm_With_90deg_Stop_Clevis")
    for a in (90, 180, 270):
        root.occurrences.addExistingComponent(comp, matrix(angle_deg=a, tz=ARM_Z))
    return occ, comp, body


def build_bucket(root, tm):
    transform = matrix(tx=PIVOT_RADIUS, tz=ARM_Z + PIVOT_Z_LOCAL)
    occ, comp = add_component(root, "04_SWING_BUCKET_MASTER_x4", transform)

    # Holder is open at the pivot/mouth and closed at its distal end.
    bucket = cylinder(
        tm,
        (BUCKET_MOUTH_OFFSET, 0, 0),
        (BUCKET_LENGTH + BUCKET_MOUTH_OFFSET, 0, 0),
        BUCKET_OD / 2,
    )
    cavity = cylinder(
        tm,
        (BUCKET_MOUTH_OFFSET - 0.5, 0, 0),
        (BUCKET_LENGTH, 0, 0),
        BUCKET_ID / 2,
    )
    cut(tm, bucket, cavity)

    # Tangential pivot lug at the tube mouth.
    # Extend the lug inboard so it can carry the hard-stop crossbar onto the
    # fork rails without the crossbar intersecting the clevis ears.
    lug = box(tm, (-6, 0, 0), (38, 24, 36))
    join(tm, bucket, lug)
    pin_hole = cylinder(tm, (0, -14, 0), (0, 14, 0), 1.7)
    cut(tm, bucket, pin_hole)

    # Wide printed tab lands on both fork rails at exactly horizontal. It clears
    # the rails when the bucket hangs vertically.
    stop = box(tm, (-20, 0, -18), (10, 38, 4))
    join(tm, bucket, stop)
    body = add_body(comp, bucket, "Swing_Bucket_15mL_90deg_Stop")

    for a in (90, 180, 270):
        tx = PIVOT_RADIUS * math.cos(math.radians(a))
        ty = PIVOT_RADIUS * math.sin(math.radians(a))
        root.occurrences.addExistingComponent(
            comp, matrix(angle_deg=a, tx=tx, ty=ty, tz=ARM_Z + PIVOT_Z_LOCAL)
        )
    return occ, comp, body


def build_hardware(root, tm):
    _, comp = add_component(root, "05_REFERENCE_HARDWARE_NOT_PRINTED")
    shaft = cylinder(tm, (0, 0, 40), (0, 0, 140), 4)
    add_body(comp, shaft, "8mm_Shaft_100mm")
    for z, name in ((40, "608ZZ_Lower"), (113, "608ZZ_Upper")):
        bearing = ring(tm, z, z + 7, 11, 4)
        add_body(comp, bearing, name)
    for i, a in enumerate((0, 90, 180, 270), 1):
        x = PIVOT_RADIUS * math.cos(math.radians(a))
        y = PIVOT_RADIUS * math.sin(math.radians(a))
        t = (-math.sin(math.radians(a)), math.cos(math.radians(a)))
        pin = cylinder(
            tm,
            (x - 21 * t[0], y - 21 * t[1], ARM_Z + PIVOT_Z_LOCAL),
            (x + 21 * t[0], y + 21 * t[1], ARM_Z + PIVOT_Z_LOCAL),
            1.5,
        )
        add_body(comp, pin, f"M3_Pivot_Pin_{i}")


def build_motor_options(root, tm):
    _, direct_comp = add_component(root, "06A_DIRECT_DRIVE_OPTION", matrix(tx=-150, ty=-150, tz=0))
    plate = box(tm, (0, 0, 3), (55, 55, 6))
    cut(tm, plate, cylinder(tm, (0, 0, -1), (0, 0, 8), 6))
    for x, y in ((-8, -9.5), (-8, 9.5), (8, -9.5), (8, 9.5)):
        drill_z(tm, plate, x, y, -1, 8)
    for x, y in ((-23, -23), (-23, 23), (23, -23), (23, 23)):
        drill_z(tm, plate, x, y, -1, 8)
    direct_plate = add_body(direct_comp, plate, "Direct_Drive_Motor_Plate_A2212")

    coupler = cylinder(tm, (0, 0, 0), (0, 0, 22), 8)
    cut(tm, coupler, cylinder(tm, (0, 0, -1), (0, 0, 11.2), 1.65))
    cut(tm, coupler, cylinder(tm, (0, 0, 10.8), (0, 0, 23), 4.1))
    # Radial M3 clamp bores on both shaft sides.
    cut(tm, coupler, cylinder(tm, (-9, 0, 6), (9, 0, 6), 1.45))
    cut(tm, coupler, cylinder(tm, (-9, 0, 17), (9, 0, 17), 1.45))
    direct_coupler = add_body(direct_comp, coupler, "Direct_Coupler_3p17_to_8mm")

    _, gear_comp = add_component(root, "06B_5TO1_GEAR_OPTION", matrix(tx=150, ty=-150, tz=0))
    gear_plate = box(tm, (18, 0, 3), (80, 55, 6))
    for cx in (0, 36):
        for dx, dy in ((-8, -9.5), (-8, 9.5), (8, -9.5), (8, 9.5)):
            drill_z(tm, gear_plate, cx + dx, dy, -1, 8)
    gear_plate_body = add_body(gear_comp, gear_plate, "Gear_Drive_Slotted_Motor_Plate")

    # Prototype PETG 1.0-module gear envelopes. Tooth flanks must be checked
    # with a validated involute add-in before sustained operation.
    driven = cylinder(tm, (0, 0, 0), (0, 0, 6), 29)
    for i in range(60):
        a = 2 * math.pi * i / 60
        rdir, tdir = (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0)
        tooth = box(tm, (30 * rdir[0], 30 * rdir[1], 3), (3.0, 1.45, 6), rdir, tdir)
        join(tm, driven, tooth)
    cut(tm, driven, cylinder(tm, (0, 0, -1), (0, 0, 7), 4.1))
    for a in (45, 135, 225, 315):
        drill_z(tm, driven, 12 * math.cos(math.radians(a)), 12 * math.sin(math.radians(a)), -1, 7)
    driven_body = add_body(gear_comp, driven, "Driven_Gear_60T_Module1_PROTOTYPE")

    pinion = cylinder(tm, (36, 0, 0), (36, 0, 6), 5)
    for i in range(12):
        a = 2 * math.pi * i / 12
        rdir, tdir = (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0)
        tooth = box(tm, (36 + 6 * rdir[0], 6 * rdir[1], 3), (3.0, 1.55, 6), rdir, tdir)
        join(tm, pinion, tooth)
    cut(tm, pinion, cylinder(tm, (36, 0, -1), (36, 0, 7), 1.65))
    pinion_body = add_body(gear_comp, pinion, "Motor_Pinion_12T_Module1_PROTOTYPE")
    return direct_plate, direct_coupler, gear_plate_body, driven_body, pinion_body


def export_body(export_mgr, root, body, filename):
    path = os.path.join(STL_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
    comp = body.parentComponent
    target_occ = None
    for occ in root.allOccurrences:
        if occ.component == comp:
            target_occ = occ
            break
    if target_occ is None:
        opts = export_mgr.createSTLExportOptions(body, path)
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        export_mgr.execute(opts)
        return

    body_index = -1
    for i in range(comp.bRepBodies.count):
        if comp.bRepBodies.item(i).entityToken == body.entityToken:
            body_index = i
            break
    if body_index < 0:
        raise RuntimeError("Could not resolve component body for STL export")

    original_transform = target_occ.transform
    target_occ.transform = adsk.core.Matrix3D.create()
    vis = []
    for i in range(target_occ.bRepBodies.count):
        proxy = target_occ.bRepBodies.item(i)
        vis.append(proxy.isVisible)
        proxy.isVisible = i == body_index
    try:
        opts = export_mgr.createSTLExportOptions(target_occ, path)
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        export_mgr.execute(opts)
    finally:
        for i, was_visible in enumerate(vis):
            target_occ.bRepBodies.item(i).isVisible = was_visible
        target_occ.transform = original_transform


def save_views(app, root):
    hidden = []
    for occ in root.occurrences:
        if occ.component.name in ("06A_DIRECT_DRIVE_OPTION", "06B_5TO1_GEAR_OPTION"):
            hidden.append((occ, occ.isLightBulbOn))
            occ.isLightBulbOn = False
    viewport = app.activeViewport
    viewport.fit()
    adsk.doEvents()
    viewport.saveAsImageFile(os.path.join(VIEW_DIR, "assembly_iso.png"), 1600, 1200)

    camera = viewport.camera
    camera.isSmoothTransition = False
    camera.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    camera.eye = p(0, 0, 800)
    camera.target = p(0, 0, 50)
    camera.upVector = v(0, 1, 0)
    viewport.camera = camera
    viewport.fit()
    adsk.doEvents()
    viewport.saveAsImageFile(os.path.join(VIEW_DIR, "assembly_top.png"), 1600, 1200)

    camera = viewport.camera
    camera.isSmoothTransition = False
    camera.eye = p(0, -800, 110)
    camera.target = p(0, 0, 50)
    camera.upVector = v(0, 0, 1)
    viewport.camera = camera
    viewport.fit()
    adsk.doEvents()
    viewport.saveAsImageFile(os.path.join(VIEW_DIR, "assembly_front.png"), 1600, 1200)

    # Temporarily show the gravity/rest position. The Fusion archive remains in
    # the horizontal at-speed position; transforms are restored after capture.
    bucket_occs = [
        occ for occ in root.occurrences
        if occ.component.name == "04_SWING_BUCKET_MASTER_x4"
    ]
    bucket_transforms = [(occ, occ.transform.copy()) for occ in bucket_occs]
    for occ in bucket_occs:
        tr = occ.transform.translation
        tx, ty, tz = tr.x * 10.0, tr.y * 10.0, tr.z * 10.0
        angle = math.atan2(ty, tx)
        radial = v(math.cos(angle), math.sin(angle), 0)
        tangential = v(-math.sin(angle), math.cos(angle), 0)
        rest = adsk.core.Matrix3D.create()
        rest.setWithCoordinateSystem(p(tx, ty, tz), v(0, 0, -1), tangential, radial)
        occ.transform = rest

    camera = viewport.camera
    camera.isSmoothTransition = False
    camera.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    camera.eye = p(420, -520, 300)
    camera.target = p(0, 0, 90)
    camera.upVector = v(0, 0, 1)
    viewport.camera = camera
    viewport.fit()
    adsk.doEvents()
    viewport.saveAsImageFile(os.path.join(VIEW_DIR, "assembly_rest_iso.png"), 1600, 1200)
    for occ, transform in bucket_transforms:
        occ.transform = transform
    for occ, was_on in hidden:
        occ.isLightBulbOn = was_on


def run_build(app, design, root):
    os.makedirs(STL_DIR, exist_ok=True)
    os.makedirs(VIEW_DIR, exist_ok=True)
    add_parameters(design)
    add_radius_reference(root)
    tm = adsk.fusion.TemporaryBRepManager.get()

    _, _, chassis = build_chassis(root, tm)
    _, _, hub = build_hub(root, tm)
    _, _, arm = build_arm(root, tm)
    _, _, bucket = build_bucket(root, tm)
    build_hardware(root, tm)
    direct_plate, direct_coupler, gear_plate, driven, pinion = build_motor_options(root, tm)

    root.attributes.add("BLOOM-2", "Purpose", "PBMC isolation over Ficoll density gradient")
    root.attributes.add("BLOOM-2", "DesignRCF", "400 x g")
    root.attributes.add("BLOOM-2", "DesignRPM", f"{DESIGN_RPM:.1f} rpm = {RESULTING_RCF:.3f} x g at 150 mm mid-fluid radius")
    root.attributes.add("BLOOM-2", "BucketMotion", "Free swing vertical to horizontal; M3 pivot; printed 90 degree hard stop")
    root.attributes.add("BLOOM-2", "RestClearance", "Lowest bucket point 40 mm above chassis base plane")
    root.attributes.add("BLOOM-2", "Safety", "Prototype only; dynamically balance and contain in lidded steel pot before powered testing")

    export_mgr = design.exportManager
    for body, filename in (
        (chassis, "01_chassis_bearing_tower.stl"),
        (hub, "02_rotor_hub.stl"),
        (arm, "03_rotor_arm_PRINT_4.stl"),
        (bucket, "04_swing_bucket_PRINT_4.stl"),
        (direct_plate, "06a_direct_motor_plate.stl"),
        (direct_coupler, "06a_direct_coupler_3p17_to_8mm.stl"),
        (gear_plate, "06b_gear_motor_plate.stl"),
        (driven, "06b_driven_gear_60T_PROTOTYPE.stl"),
        (pinion, "06b_motor_pinion_12T_PROTOTYPE.stl"),
    ):
        export_body(export_mgr, root, body, filename)

    step_path = os.path.join(OUT_DIR, "BLOOM-2_centrifuge_assembly.step")
    f3d_path = os.path.join(OUT_DIR, "BLOOM-2_centrifuge_parametric.f3d")
    for path in (step_path, f3d_path):
        if os.path.exists(path):
            os.remove(path)
    export_mgr.execute(export_mgr.createSTEPExportOptions(step_path))
    export_mgr.execute(export_mgr.createFusionArchiveExportOptions(f3d_path))
    save_views(app, root)
    return {
        "rpm": DESIGN_RPM,
        "rcf": TARGET_RCF,
        "radius_mm": ROTOR_RADIUS,
        "pivot_radius_mm": PIVOT_RADIUS,
        "rotor_tip_radius_mm": PIVOT_RADIUS + BUCKET_LENGTH + BUCKET_MOUTH_OFFSET,
        "minimum_pot_id_mm": 2 * (PIVOT_RADIUS + BUCKET_LENGTH + BUCKET_MOUTH_OFFSET + 15),
        "output_dir": OUT_DIR,
    }
