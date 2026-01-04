# microscale/config.py
TARGET_RATIO = 1.164  # width / height
SCALE_HEIGHT = 48  # pixels to remove from bottom if too tall
CROPPED_SUFFIX = "#"  # suffix for cropped files
SCALED_SUFFIX = "_"  # suffix for scaled files
PIX_PER_MM = {
    "n1": 426,
    "n2": 683,
    "n4": 1376,
    "n10": 3345,
    "n20": 6924,
    "n40": 13530,
    "m2": 628,
    "m4": 1200,
    "m10": 2324,
    "m20": 4218,
    "l2": 628,
    "l4": 1200,
    "l10": 2324,
    "l20": 4218,
    "o2": 535,
    "o4": 1200,
    "o10": 2324,
    "o20": 4218,
}
