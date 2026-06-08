"""
This file contains the functions necessary for
creating the interactive response dial at the end of a trial.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import event, sound, core
from psychopy.hardware.keyboard import Keyboard
from time import time
from eyetracker import get_trigger
from stimuli import draw_fixation_dot, COLOUR_HEIGHT
from math import floor


def evaluate_auditory_response(target_frequency, response_frequency, freqs):
    freq_diff = response_frequency - target_frequency
    freq_diff_abs = abs(freq_diff)
    performance = freqs.index(response_frequency) - freqs.index(target_frequency)
    sign = "+" if performance > 0 else ""
    return {
        "frequency_offset": round(freq_diff),
        "frequency_diff_abs": round(freq_diff_abs),
        "performance_abs": abs(performance),
        "performance": f"{sign}{performance}",
    }


def evaluate_visual_response(target_hue, response_hue, hues):
    colour_diff = response_hue - target_hue
    colour_diff_abs = abs(colour_diff)
    performance = hues.index(response_hue) - hues.index(target_hue)
    sign = "+" if performance > 0 else ""
    return {
        "colour_offset": round(colour_diff),
        "colour_diff_abs": round(colour_diff_abs),
        "performance_abs": abs(performance),
        "performance": f"{sign}{performance}",
    }


def move_marker(marker, current_colour, colours, settings):
    height = settings["deg2pix"](COLOUR_HEIGHT)
    total_height = len(colours) * height
    start_y = -total_height / 2

    # The marker should be at the same spot as the selected colour
    target_y = start_y + (colours.index(current_colour) * height) + (height / 2)
    marker.pos = (0, target_y)
    marker.fillColor = current_colour

    return marker


def get_auditory_response(
    target_pitch,
    target_item,
    target_position,
    block_type,
    stimuli,
    settings,
    testing,
    eyetracker,
):
    keyboard: Keyboard = settings["keyboard"]

    # Check for pressed 'q'
    check_quit(keyboard)

    # Check if _any_ keys were prematurely pressed
    prematurely_pressed = [(k.value, k.t) for k in keyboard.getKeys(clear=False)]
    keyboard.clearEvents()

    # Set initial settings
    freqs = settings["frequencies"]
    idx = floor(len(freqs) / 2)  # use middle index to start
    responded = False

    # Show response can start
    draw_fixation_dot(stimuli["fixation_dot"], [-1, -1, -1])
    settings["window"].flip()

    # These timing systems should start at the same time, this is almost true
    idle_reaction_time_start = time()
    keyboard.clock.reset()

    # Wait for response to start
    first_keys = keyboard.waitKeys(
        keyList=["down", "up", "space", "q"], waitRelease=True
    )
    response_started = time()
    keys = first_keys  # use first key press for first tone generation

    if not testing and eyetracker:
        trigger = get_trigger(
            "response_onset", target_item, block_type, target_position
        )
        eyetracker.tracker.send_message(f"trig{trigger}")

    # Let participant change tone frequency until space bar is pressed
    while not responded:

        if "space" in keys:
            responded = True
            response_freq = freqs[idx]
            response_idx = idx

        elif "q" in keys:
            raise KeyboardInterrupt()

        elif "down" in keys or "up" in keys:
            old_idx = idx

            if "down" in keys:
                idx = max(idx - 1, 0)
            elif "up" in keys:
                idx = min(idx + 1, len(freqs) - 1)

            # Start new tone first, then stop old one (avoids clicks)
            stimuli["sounds"][
                (freqs[idx], "both")
            ].stop()  # ensure tone is back to beginning first
            stimuli["sounds"][(freqs[idx], "both")].play()
            core.wait(0.005)  # 5 ms overlap
            if idx != old_idx:
                stimuli["sounds"][(freqs[old_idx], "both")].stop()

        core.wait(0.01)
        keys = keyboard.getKeys(keyList=["down", "up", "space"])

    # Compute both reaction times
    response_time = time() - response_started
    idle_reaction_time = response_started - idle_reaction_time_start

    if not testing and eyetracker:
        trigger = get_trigger(
            "response_offset", target_item, block_type, target_position
        )
        eyetracker.tracker.send_message(f"trig{trigger}")

    # Make sure keystrokes made during this trial don't influence the next
    keyboard.clearEvents()

    return {
        "idle_reaction_time_in_ms": round(idle_reaction_time * 1000, 2),
        "response_time_in_ms": round(response_time * 1000, 2),
        "first_key_pressed": first_keys[0].name,
        "response_freq": response_freq,
        "response_idx": response_idx,
        "premature_pressed": True if prematurely_pressed else False,
        "premature_key": prematurely_pressed[0][0] if prematurely_pressed else None,
        "premature_timing": (
            round(prematurely_pressed[0][1] * 1000, 2) if prematurely_pressed else None
        ),
        **evaluate_auditory_response(target_pitch, response_freq, freqs),
    }


def get_visual_response(
    target_hue,
    target_item,
    target_position,
    block_type,
    stimuli,
    settings,
    testing,
    eyetracker,
):
    keyboard: Keyboard = settings["keyboard"]

    # Check for pressed 'q'
    check_quit(keyboard)

    # Check if _any_ keys were prematurely pressed
    prematurely_pressed = [(k.value, k.t) for k in keyboard.getKeys(clear=False)]
    keyboard.clearEvents()

    # Set initial settings
    colour_ladder = stimuli["colour_ladder"]
    marker = stimuli["marker"]
    colours = settings["colours"]
    idx = 5
    responded = False

    # Show response can start
    draw_fixation_dot(stimuli["fixation_dot"], [-1, -1, -1])
    settings["window"].flip()

    # These timing systems should start at the same time, this is almost true
    idle_reaction_time_start = time()
    keyboard.clock.reset()

    # Wait for response to start
    first_keys = keyboard.waitKeys(
        keyList=["down", "up", "space", "q"], waitRelease=True
    )
    response_started = time()
    keys = first_keys  # use first key press for first tone generation

    if not testing and eyetracker:
        trigger = get_trigger(
            "response_onset", target_item, block_type, target_position
        )
        eyetracker.tracker.send_message(f"trig{trigger}")

    # Let participant change colour until space bar is pressed
    while not responded:

        if "space" in keys:
            responded = True
            response_colour = colours[idx]
            response_idx = idx
            response_hue = response_colour[0]

        elif "q" in keys:
            raise KeyboardInterrupt()

        elif "down" in keys or "up" in keys:

            if "down" in keys:
                idx = max(idx - 1, 0)
            elif "up" in keys:
                idx = min(idx + 1, len(colours) - 1)

            # Draw colour wheel, fixation dot and new marker position
            for step in colour_ladder:
                step.draw()
            marker = move_marker(marker, colours[idx], colours, settings)
            marker.draw()
            draw_fixation_dot(stimuli["fixation_dot"], [-1, -1, -1])

            settings["window"].flip()

        core.wait(0.01)
        keys = keyboard.getKeys(keyList=["down", "up", "space"])

    # Compute both reaction times
    response_time = time() - response_started
    idle_reaction_time = response_started - idle_reaction_time_start

    if not testing and eyetracker:
        trigger = get_trigger(
            "response_offset", target_item, block_type, target_position
        )
        eyetracker.tracker.send_message(f"trig{trigger}")

    # Make sure keystrokes made during this trial don't influence the next
    keyboard.clearEvents()

    return {
        "idle_reaction_time_in_ms": round(idle_reaction_time * 1000, 2),
        "response_time_in_ms": round(response_time * 1000, 2),
        "first_key_pressed": first_keys[0].name,
        "response_colour": response_colour,
        "response_hue": response_hue,
        "response_idx": response_idx,
        "premature_pressed": True if prematurely_pressed else False,
        "premature_key": prematurely_pressed[0][0] if prematurely_pressed else None,
        "premature_timing": (
            round(prematurely_pressed[0][1] * 1000, 2) if prematurely_pressed else None
        ),
        **evaluate_visual_response(target_hue, response_hue, settings["hues"]),
    }


def wait_for_key(key_list, keyboard):
    keyboard: Keyboard = keyboard
    keyboard.clearEvents()
    keys = keyboard.waitKeys(keyList=key_list)

    return keys


def check_quit(keyboard):
    if keyboard.getKeys("q", clear=False):
        raise KeyboardInterrupt()
