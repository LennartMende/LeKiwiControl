from enum import Enum

CLOSED_PENCIL = {
    'arm_shoulder_pan.pos': -6.294760648322651,
    'arm_shoulder_lift.pos': -19.680403700588727,
    'arm_elbow_flex.pos': 97.93536804308798,
    'arm_wrist_flex.pos': -32.76231263383298,
    'arm_wrist_roll.pos': 52.62515262515262,
    'arm_gripper.pos': 0.8771929824561403
}

CLOSED_PENCIL_PAINT_LIFTED = {
    'arm_shoulder_pan.pos': -6.294760648322651,
    'arm_shoulder_lift.pos': -18.680403700588727,
    'arm_elbow_flex.pos': 97.1,
    'arm_wrist_flex.pos': -39.5,
    'arm_wrist_roll.pos': 52.62515262515262,
    'arm_gripper.pos': 0.8771929824561403
}

CLOSED_PENCIL_PAINT = {
    'arm_shoulder_pan.pos': -6.294760648322651,
    'arm_shoulder_lift.pos': -18.680403700588727,
    'arm_elbow_flex.pos': 97.1,
    'arm_wrist_flex.pos': -30.5,
    'arm_wrist_roll.pos': 52.62515262515262,
    'arm_gripper.pos': 0.8771929824561403
}

HALF_OPEN_PENCIL  = {
    'arm_shoulder_pan.pos': -6.294760648322651,
    'arm_shoulder_lift.pos': -19.680403700588727,
    'arm_elbow_flex.pos': 97.93536804308798,
    'arm_wrist_flex.pos': -32.76231263383298,
    'arm_wrist_roll.pos': 52.62515262515262,
    'arm_gripper.pos': 22.00956937799043
}

OPEN_PENCIL = {
    'arm_shoulder_pan.pos': -6.294760648322651,
    'arm_shoulder_lift.pos': -19.680403700588727,
    'arm_elbow_flex.pos': 97.93536804308798,
    'arm_wrist_flex.pos': -32.76231263383298,
    'arm_wrist_roll.pos': 52.62515262515262,
    'arm_gripper.pos': 96.7304625199362
}

CLOSED_REST = {
    'arm_shoulder_pan.pos': -6.294760648322651,
    'arm_shoulder_lift.pos': -98.99074852817493,
    'arm_elbow_flex.pos': 98.83303411131058,
    'arm_wrist_flex.pos': 50.920770877944335,
    'arm_wrist_roll.pos': 0.952380952380949,
    'arm_gripper.pos': 0.8771929824561403
}

OPEN_REST = {
    'arm_shoulder_pan.pos': -2.902374670184699,
    'arm_shoulder_lift.pos': -98.90664423885619,
    'arm_elbow_flex.pos': 98.74326750448833,
    'arm_wrist_flex.pos': 51.26338329764454,
    'arm_wrist_roll.pos': 0.9035409035409003,
    'arm_gripper.pos': 97.4481658692185
}

CLOSED_STRETCHED_TO_SKY = {
    'arm_shoulder_pan.pos': -10.89332830757634,
    'arm_shoulder_lift.pos': -0.2523128679562632,
    'arm_elbow_flex.pos': -79.62298025134649,
    'arm_wrist_flex.pos': -0.9850107066381071,
    'arm_wrist_roll.pos': 0.952380952380949,
    'arm_gripper.pos': 0.8771929824561403
}

OPEN_STRETCHED_TO_SKY = {
    'arm_shoulder_pan.pos': -10.89332830757634,
    'arm_shoulder_lift.pos': 3.6164844407064862,
    'arm_elbow_flex.pos': -83.3931777378815,
    'arm_wrist_flex.pos': -1.0706638115631648,
    'arm_wrist_roll.pos': 1.098901098901095,
    'arm_gripper.pos': 97.4481658692185
}

CLOSED_PENCIL2 = {'arm_shoulder_pan.pos': -4.33471541650961,
    'arm_shoulder_lift.pos': 50.04205214465938,
    'arm_elbow_flex.pos': 63.73429084380609,
    'arm_wrist_flex.pos': -97.4304068522484,
    'arm_wrist_roll.pos': 50.13431013431014, 
    'arm_gripper.pos': 0.6379585326953748
}

HALF_OPEN_PENCIL2 = {'arm_shoulder_pan.pos': -4.33471541650961,
    'arm_shoulder_lift.pos': 50.04205214465938,
    'arm_elbow_flex.pos': 63.73429084380609,
    'arm_wrist_flex.pos': -97.4304068522484,
    'arm_wrist_roll.pos': 50.13431013431014, 
    'arm_gripper.pos': 22.00956937799043
 }

OPEN_PENCIL2 = {'arm_shoulder_pan.pos': -4.33471541650961,
    'arm_shoulder_lift.pos': 50.04205214465938,
    'arm_elbow_flex.pos': 63.73429084380609,
    'arm_wrist_flex.pos': -97.4304068522484,
    'arm_wrist_roll.pos': 50.13431013431014, 
    'arm_gripper.pos': 96.7304625199362
 }

class DefaultArmPose(Enum):
    """Fasst alle standardmäßigen Armposen zusammen"""
    CLOSED_PENCIL = CLOSED_PENCIL
    CLOSED_PENCIL_PAINT_LIFTED = CLOSED_PENCIL_PAINT_LIFTED
    CLOSED_PENCIL_PAINT = CLOSED_PENCIL_PAINT
    HALF_OPEN_PENCIL = HALF_OPEN_PENCIL
    OPEN_PENCIL = OPEN_PENCIL
    CLOSED_REST = CLOSED_REST
    OPEN_REST = OPEN_REST
    OPEN_STRETCHED_TO_SKY = OPEN_STRETCHED_TO_SKY
    CLOSED_STRETCHED_TO_SKY = CLOSED_STRETCHED_TO_SKY
    CLOSED_PENCIL2 = CLOSED_PENCIL2
    HALF_OPEN_PENCIL2 = HALF_OPEN_PENCIL2
    OPEN_PENCIL2 = OPEN_PENCIL2