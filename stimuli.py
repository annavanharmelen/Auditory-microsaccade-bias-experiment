"""
This file contains the functions necessary for
creating the fixation cross and the bar stimuli.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual, sound, core
import numpy as np

DOT_SIZE = 0.15  # radius of circle
OBJECT_SIZE = 0.5  # radius of circle
ECCENTRICITY = 7.5
ITEM_SIZE = 1
COLOUR_WIDTH = 2
COLOUR_HEIGHT = 1

AUDIO_SAMPLE_RATE = 44100


def initialise_all_stimuli(settings):
    cached_sounds = {}

    tone_duration = 0.25  # in seconds
    sample_times = np.linspace(
        0, tone_duration, int(tone_duration * AUDIO_SAMPLE_RATE), endpoint=False
    )

    # Ramp tone up and down
    ramp_ms = 5  # duration in ms
    ramp_samples = int(AUDIO_SAMPLE_RATE * ramp_ms / 1000)
    ramp_up = np.linspace(0, 1, ramp_samples)
    ramp_down = np.linspace(1, 0, ramp_samples)

    # Create zero channel (for left-only and right-only sounds)
    zeros = np.zeros_like(sample_times, dtype=np.float32)

    # Create all 22 possible stereo tones
    for frequency in settings["frequencies"]:
        # Create mono waveform
        waveform = np.sin(2 * np.pi * frequency * sample_times)

        # Apply ramping
        waveform[:ramp_samples] *= ramp_up
        waveform[-ramp_samples:] *= ramp_down

        # Save ramped waveform in right format
        waveform = waveform.astype(np.float32)

        # Create stereo array
        left_stereo = np.stack([waveform, zeros], axis=1)
        right_stereo = np.stack([zeros, waveform], axis=1)

        # Cache sound objects
        cached_sounds[(frequency, "left")] = sound.Sound(
            left_stereo, stereo=True, sampleRate=AUDIO_SAMPLE_RATE
        )
        cached_sounds[(frequency, "right")] = sound.Sound(
            right_stereo, stereo=True, sampleRate=AUDIO_SAMPLE_RATE
        )
        cached_sounds[(frequency, "both")] = sound.Sound(
            waveform, stereo=False, sampleRate=AUDIO_SAMPLE_RATE
        )

    # Draw the colour ladder using segments
    colour_ladder = []
    bar_width = settings["deg2pix"](COLOUR_WIDTH)
    bar_height = settings["deg2pix"](COLOUR_HEIGHT)
    colours = settings["colours"]
    total_height = len(colours) * bar_height
    start_y = -total_height / 2  # starting at the bottom to keep the ladder centered

    for i, colour in enumerate(colours):
        # Calculate position of step in ladder
        y_center = start_y + (i * bar_height) + (bar_height / 2)

        # Create a wedge for each segment
        step = visual.Rect(
            settings["window"],
            width=bar_width,
            height=bar_height,
            pos=(0, y_center),
            fillColor=colour,
            lineColor=None,
            colorSpace="hsv",
        )
        colour_ladder.append(step)

    # Create a marker for the selected colour preview
    marker = visual.Rect(
        settings["window"],
        width=bar_width + 50,
        height=bar_height,
        fillColor=None,
        lineColor=(1, 0, 1),
        colorSpace="hsv",
    )

    # Make fixation dot
    fixation_dot = visual.Circle(
        win=settings["window"],
        units="pix",
        radius=settings["deg2pix"](DOT_SIZE),
        edges=20,
        pos=(0, 0),
        fillColor="#eaeaea",
    )

    # Make visual object
    visual_object = visual.Circle(
        win=settings["window"],
        units="pix",
        radius=settings["deg2pix"](OBJECT_SIZE),
        pos=(0, 0),
        fillColor="#eaeaea",
        colorSpace="hsv",
    )

    return {
        "sounds": cached_sounds,
        "fixation_dot": fixation_dot,
        "visual_object": visual_object,
        "colour_ladder": colour_ladder,
        "marker": marker,
    }


def show_text(input, window, pos=(0, 0), colour="#ffffff"):
    textstim = visual.TextStim(
        win=window, font="Aptos", text=input, color=colour, pos=pos, height=22
    )

    textstim.draw()


def draw_fixation_dot(fixation_dot, colour="#eaeaea"):
    fixation_dot.fillColor = colour
    fixation_dot.draw()


def draw_visual_object(visual_object, hue, position, settings):
    if position == "left":
        pos = (-settings["deg2pix"](ECCENTRICITY), 0)
    elif position == "right":
        pos = (settings["deg2pix"](ECCENTRICITY), 0)
    else:
        pos = (0, 0)

    visual_object.fillColor = settings["colours"][settings["hues"].index(hue)]
    visual_object.pos = pos
    visual_object.draw()


def create_visual_stimulus_frame(visual_object, hue, position, fixation_dot, settings):
    draw_fixation_dot(fixation_dot)
    draw_visual_object(visual_object, hue, position, settings)


def create_cue_frame(target_item, fixation_dot, settings):
    draw_fixation_dot(fixation_dot)
    show_text(
        target_item,
        settings["window"],
        pos=(0, settings["deg2pix"](0)),
        colour="#000000",
    )


def create_feedback_frame(main_feedback, fixation_dot, settings):
    draw_fixation_dot(fixation_dot)
    show_text(
        f"{main_feedback}",
        settings["window"],
        (0, settings["deg2pix"](0.35)),
    )
