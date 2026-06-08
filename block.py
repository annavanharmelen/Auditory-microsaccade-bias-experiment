"""
This file contains the functions necessary for
creating and running a full block of trials start-to-finish.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

import random
from stimuli import show_text
from response import wait_for_key


def create_trial_list(n_trials):
    if n_trials % 4 != 0:
        raise Exception(
            "Expected number of trials to be divisible by 4, otherwise perfect factorial combinations are not possible."
        )

    # Generate equal distribution of stimulus locations
    target_position = 2 * (n_trials // 2 * ["left"] + n_trials // 2 * ["right"])

    # Generate equal distribution of target items
    target_item = n_trials // 2 * [1, 2]

    # Create trial parameters for all trials
    trials = list(zip(target_position, target_item))
    random.shuffle(trials)

    return trials


def block_break(current_block, n_blocks, avg_score, settings, eyetracker):
    blocks_left = n_blocks - current_block

    show_text(
        f"In the previous block, your reports were on average off by {avg_score}"
        f"\n\nYou just finished block {current_block}, you {'only ' if blocks_left == 1 else ''}"
        f"have {blocks_left} block{'s' if blocks_left != 1 else ''} left. "
        "Take a break if you want to, but try not to move your head during this break."
        "\n\nPress SPACE when you're ready to continue.",
        settings["window"],
    )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            eyetracker.start()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    # Make sure the keystroke from starting the experiment isn't saved
    settings["keyboard"].clearEvents()

    return False


def block_switch_instructions(upcoming_block, settings, eyetracker):
    if upcoming_block == "speakers":
        show_text(
            f"Please remove your headphones." "\n\nWhen done, press SPACE to continue.",
            settings["window"],
        )
    elif upcoming_block == "headphones":
        show_text(
            f"Please put on your headphones." "\n\nWhen done, press SPACE to continue.",
            settings["window"],
        )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            eyetracker.start()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    # Make sure the keystroke from starting the experiment isn't saved
    settings["keyboard"].clearEvents()

    return False


def long_break(n_blocks, avg_score, settings, eyetracker):
    show_text(
        f"In the previous block, your reports were on average off by {avg_score}."
        f"\n\nYou're halfway through! You have {n_blocks // 2} blocks left. "
        "Now is the time to take a longer break. Maybe get up, stretch, walk around."
        "\n\nPress SPACE whenever you're ready to continue again.",
        settings["window"],
    )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    # Make sure the keystroke from starting the experiment isn't saved
    settings["keyboard"].clearEvents()

    return False


def finish(n_blocks, settings):
    show_text(
        f"Congratulations! You successfully finished all {n_blocks} blocks!"
        "You're completely done now. Press SPACE to exit the experiment.",
        settings["window"],
    )
    settings["window"].flip()

    wait_for_key(["space"], settings["keyboard"])


def quick_finish(settings):
    settings["window"].flip()
    show_text(
        f"You've exited the experiment. Press SPACE to close this window.",
        settings["window"],
    )
    settings["window"].flip()

    wait_for_key(["space"], settings["keyboard"])
