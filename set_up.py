"""
This file contains the functions necessary for
seting up the computer.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual, prefs
from psychopy.hardware.keyboard import Keyboard
from math import degrees, atan2, pi


def get_monitor_and_dir(testing: bool):
    prefs.hardware["audioLib"] = ["PTB", "sounddevice", "pyo", "pygame"]

    if testing:
        # laptop
        # prefs.hardware["audioDevice"] = "Speakers (Realtek(R) Audio)"
        monitor = {
            "resolution": (2880, 1800),  # in pixels
            "Hz": 120,  # screen refresh rate in Hz
            "width": 30,  # in cm
            "distance": 50,  # in cm
        }

        directory = r"../../Data/test2/"

    else:
        # lab
        # prefs.hardware['audioDevice'] = 'XG248Q (2- NVIDIA High Definition Audio)'
        # prefs.hardware['audioDevice'] = 'Headphones (Realtek(R) Audio)'
        prefs.hardware["audioDevice"] = "Speakers (Realtek(R) Audio)"
        monitor = {
            "resolution": (1920, 1080),  # in pixels
            "Hz": 239,  # screen refresh rate in Hz
            "width": 53,  # in cm
            "distance": 70,  # in cm
        }

        directory = r"C:/Users/Anna_vidi/Desktop/Auditory data/"

    return monitor, directory


def get_settings(monitor: dict, directory):
    # Initialise psychopy window
    window = visual.Window(
        color=([-0.5, -0.5, -0.5]),
        size=monitor["resolution"],
        units="pix",
        fullscr=True,
    )

    # Calculate number of visual degrees per pixel on the screen
    degrees_per_pixel = degrees(atan2(0.5 * monitor["width"], monitor["distance"])) / (
        0.5 * monitor["resolution"][0]
    )

    # Create list of used frequencies
    frequencies = [300, 316, 332, 350, 368, 387, 408, 429, 451, 475, 500]

    # Determine colour range
    hues = [105, 90, 75, 60, 45, 30, 15, 0, 345, 330, 315]
    colours = [
        [
            hue,  # Hue
            0.2,  # Saturation
            0.5,  # Value
        ]
        for hue in hues
    ]

    return dict(
        window=window,
        deg2pix=lambda deg: round(deg / degrees_per_pixel),
        frequencies=frequencies,
        hues=hues,
        colours=colours,
        keyboard=Keyboard(),
        mouse=visual.CustomMouse(win=window, visible=False),
        monitor=monitor,
        directory=directory,
    )
