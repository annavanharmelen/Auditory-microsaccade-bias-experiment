"""
This file contains the functions necessary for
practising the trials and the use of the report dial.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

import random
from trial import generate_trial_characteristics
from stimuli import show_text
from response import wait_for_key
from trial import single_trial
from numpy import mean
import traceback


def practice(stimuli, block_type, eyetracker, settings):
    # Practice full trials until participant chooses to stop
    block = {"auditory": "sounds", "visual": "colours"}[block_type]

    try:
        performance = []

        # Show first screen
        show_text(
            f"Welcome!\nPress SPACE to start practicing how to reproduce {block}.",
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

        while True:
            target_position = random.choice(["left", "right"])
            target_item = random.choice([1, 2])

            trial_characteristics = generate_trial_characteristics(
                (target_position, target_item), block_type, settings
            )

            # Generate trial
            report = single_trial(
                **trial_characteristics,
                stimuli=stimuli,
                block_type=block_type,
                settings=settings,
                testing=True,
                eyetracker=None,
            )

            # Save for feedback
            performance.append(int(report["performance_abs"]))

    except KeyboardInterrupt:
        settings["window"].flip()

        if len(performance) > 0:
            avg_score = round(mean(performance), 1)
            show_text(
                f"During this practice, your reports were on average off by {avg_score}. "
                f"\n\nPress SPACE to start the experiment.",
                settings["window"],
            )
        else:
            show_text(
                f"You skipped the practice.\n\nPress SPACE to start the experiment.",
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
