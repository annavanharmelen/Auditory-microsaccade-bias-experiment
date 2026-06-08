"""
This file contains the functions necessary for
creating and running a single trial start-to-finish,
including eyetracker triggers.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual
from psychopy.core import wait
from time import time, sleep
from response import get_auditory_response, get_visual_response, check_quit
from stimuli import (
    show_text,
    draw_fixation_dot,
    create_visual_stimulus_frame,
    create_cue_frame,
    create_feedback_frame,
)
from eyetracker import get_trigger
import random


def generate_trial_characteristics(conditions, task_type, settings):
    # Extract condition information
    target_position, target_item = conditions

    distractor_position = {"left": "right", "right": "left"}[target_position]
    distractor_item = {1: 2, 2: 1}[target_item]

    # Determine stimuli depending on task_type
    if task_type == "auditory":
        stimuli_options = settings["frequencies"][:5] + settings["frequencies"][6:]
    elif task_type == "visual":
        stimuli_options = settings["hues"][:5] + settings["hues"][6:]

    # Generate random pitch OR colour for both target and distractor (cannot be the same!)
    target_idx = random.randrange(len(stimuli_options))
    distractor_idx = random.randrange(len(stimuli_options) - 1)

    if distractor_idx >= target_idx:
        distractor_idx += 1

    target_value = stimuli_options[target_idx]
    distractor_value = stimuli_options[distractor_idx]

    if target_item == 1:
        positions = [target_position, distractor_position]
        values_order = [target_value, distractor_value]
        values_idx_order = [target_idx, distractor_idx]
    else:
        positions = [distractor_position, target_position]
        values_order = [distractor_value, target_value]
        values_idx_order = [distractor_idx, target_idx]

    if target_position == "left":
        order = [target_item, distractor_item]
        values_positions = [target_value, distractor_value]
        values_idx_positions = [target_idx, distractor_idx]
    else:
        order = [distractor_item, target_item]
        values_positions = [distractor_value, target_value]
        values_idx_positions = [distractor_idx, target_idx]

    return {
        "ITI": random.randint(500, 800),
        "target_position": target_position,
        "target_item": target_item,
        "target_value": target_value,
        "target_idx": target_idx,
        "distractor_position": distractor_position,
        "distractor_item": distractor_item,
        "distractor_value": distractor_value,
        "distractor_idx": distractor_idx,
        "positions": positions,
        "values_order": values_order,
        "values_idx_order": values_idx_order,
        "order_LR": order,
        "values_positions": values_positions,
        "values_idx_positions": values_idx_positions,
    }


def do_while_showing(waiting_time, draw, window, on_flip=None):
    """
    Show whatever is drawn to the screen for exactly `waiting_time` period,
    while doing `something_to_do` in the mean time.
    On initial screen flip, also execute a function (if passed).
    """
    window.flip()
    start = time()
    if on_flip:
        on_flip()
    draw()
    wait(waiting_time - (time() - start))


def single_trial(
    ITI,
    target_position,
    target_item,
    target_value,
    target_idx,
    distractor_position,
    distractor_item,
    distractor_value,
    distractor_idx,
    positions,
    values_order,
    values_idx_order,
    order_LR,
    values_positions,
    values_idx_positions,
    stimuli,
    block_type,
    settings,
    testing,
    eyetracker=None,
):
    # Initial fixation cross to eliminate jitter caused by for loop
    draw_fixation_dot(stimuli["fixation_dot"])

    def make_stimulus_screen(idx, duration, trigger_code):
        if block_type == "auditory":
            # Auditory block: Show fixation, play sound
            draw_func = lambda: draw_fixation_dot(stimuli["fixation_dot"])
            exec_func = lambda: stimuli["sounds"][
                (values_order[idx], positions[idx])
            ].play()

        elif block_type == "visual":
            # Visual block: Show visual objects, play no sound
            draw_func = lambda: create_visual_stimulus_frame(
                stimuli["visual_object"],
                values_order[idx],
                positions[idx],
                stimuli["fixation_dot"],
                settings,
            )
            exec_func = None

        return (duration, draw_func, exec_func, trigger_code)

    # Screens contains per screen: (timing, function_to_draw(), function_to_execute(), triggercode)
    screens = [
        (0, lambda: 0 / 0, None, None),  # initial one to make life easier
        (ITI / 1000, lambda: draw_fixation_dot(stimuli["fixation_dot"]), None, None),
        make_stimulus_screen(0, 0.25, "stimulus_onset_1"),
        (0.75, lambda: draw_fixation_dot(stimuli["fixation_dot"]), None, None),
        make_stimulus_screen(1, 0.25, "stimulus_onset_2"),
        (0.75, lambda: draw_fixation_dot(stimuli["fixation_dot"]), None, None),
        (
            0.25,
            lambda: create_cue_frame(target_item, stimuli["fixation_dot"], settings),
            None,
            "cue_onset",
        ),
        (1.25, lambda: draw_fixation_dot(stimuli["fixation_dot"]), None, None),
    ]

    # !!! The timing you pass to do_while_showing is the timing for the previously drawn screen. !!!
    for index, (duration, _, _, frame) in enumerate(screens[:-1]):
        # Send trigger if not testing
        if not testing and frame:
            trigger = get_trigger(frame, target_item, block_type, target_position)
            eyetracker.tracker.send_message(f"trig{trigger}")

        # Check for pressed 'q'
        check_quit(settings["keyboard"])

        # Draw the next screen while showing the current one
        do_while_showing(
            duration, screens[index + 1][1], settings["window"], screens[index][2]
        )

    # The for loop only draws the last frame, never shows it
    # So show it here
    settings["window"].flip()
    wait(screens[-1][0])

    if block_type == "auditory":
        response = get_auditory_response(
            target_value,
            target_item,
            target_position,
            block_type,
            stimuli,
            settings,
            testing,
            eyetracker,
        )
    elif block_type == "visual":
        response = get_visual_response(
            target_value,
            target_item,
            target_position,
            block_type,
            stimuli,
            settings,
            testing,
            eyetracker,
        )

    # Show performance (and feedback on premature key usage if necessary)
    create_feedback_frame(response["performance"], stimuli["fixation_dot"], settings)

    if response["premature_pressed"] == True:
        show_text("!", settings["window"], (0, -settings["deg2pix"](0.3)))

    if not testing:
        trigger = get_trigger(
            "feedback_onset", target_item, block_type, target_position
        )
        eyetracker.tracker.send_message(f"trig{trigger}")

    settings["window"].flip()
    sleep(0.35)

    return {
        "condition_code": get_trigger(
            "stimulus_onset_1", target_item, block_type, target_position
        ),
        **response,
    }
