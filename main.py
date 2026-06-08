"""
Main script for running the 'auditory microsaccade bias' experiment
made by Anna van Harmelen, 2026

see README.md for instructions if needed
"""

# Import necessary stuff
from psychopy import logging, core
import pandas as pd
from participantinfo import get_participant_details
from set_up import get_monitor_and_dir, get_settings
from eyetracker import Eyelinker
from stimuli import initialise_all_stimuli
from trial import single_trial, generate_trial_characteristics
from time import time
from numpy import mean
from practice import practice
import datetime as dt
from block import (
    create_trial_list,
    block_break,
    long_break,
    finish,
    quick_finish,
    block_switch_instructions,
)
import traceback

N_BLOCKS = 10
TRIALS_PER_BLOCK = 32


def main():
    """
    Data formats / storage:
     - eyetracking data saved in one .edf file per session
     - all trial data saved in one .csv per session
     - subject data in one .csv (for all sessions combined)
    """

    # Set whether this is a test run or not
    testing = False

    # first things first: ignore warnings
    logging.console.setLevel(logging.ERROR)

    # Get monitor and directory information
    monitor, directory = get_monitor_and_dir(testing)

    # Get participant details and save in same file as before
    old_participants = pd.read_csv(
        rf"{directory}\participantinfo.csv",
        dtype={
            "participant_number": int,
            "session_number": int,
            "session_within_pp": int,
            "age": int,
            "start_block_type": str,
            "current_block_type": str,
            "trials_completed": str,
        },
    )
    new_participants, current_block_type = get_participant_details(
        old_participants, testing
    )

    # Initialise set-up
    settings = get_settings(monitor, directory)
    settings["keyboard"].clearEvents()

    # Connect to eyetracker and calibrate it
    if not testing:
        eyelinker = Eyelinker(
            new_participants.participant_number.iloc[-1],
            new_participants.session_number.iloc[-1],
            current_block_type[0],
            settings["window"],
            settings["directory"],
        )
        eyelinker.calibrate()

    # Start recording eyetracker
    if not testing:
        eyelinker.start()

    # Initialise stimuli
    stimuli = initialise_all_stimuli(settings)

    # Practice until participant wants to stop
    # practice(current_block_type, stimuli, None if testing else eyelinker, settings)

    # Initialise some stuff
    start_of_experiment = time()
    data = []
    current_trial = 0
    finished_early = True

    # Start experiment
    try:
        for block_nr in range(2 if testing else N_BLOCKS):
            # Pseudo-randomly create conditions and target locations (so they're weighted)
            trials = create_trial_list(4 if testing else TRIALS_PER_BLOCK)

            # Clear keyboard cache before starting again
            settings["keyboard"].clearEvents()

            # Create temporary variable for saving block performance
            block_performance = []

            # Run trials per pseudo-randomly created info
            for trial in trials:
                current_trial += 1
                start_time = time()

                trial_characteristics: dict = generate_trial_characteristics(
                    trial, current_block_type, settings
                )

                # Generate trial
                report: dict = single_trial(
                    **trial_characteristics,
                    stimuli=stimuli,
                    block_type=current_block_type,
                    settings=settings,
                    testing=testing,
                    eyetracker=None if testing else eyelinker,
                )
                end_time = time()

                # Save trial data
                data.append(
                    {
                        "trial_number": current_trial,
                        "block": block_nr + 1,
                        "block_type": current_block_type,
                        "start_time": str(
                            dt.timedelta(seconds=(start_time - start_of_experiment))
                        ),
                        "end_time": str(
                            dt.timedelta(seconds=(end_time - start_of_experiment))
                        ),
                        **trial_characteristics,
                        **report,
                    }
                )

                block_performance.append(int(report["performance_abs"]))

            # Calculate average performance score for most recent block
            avg_score = round(mean(block_performance), 1)

            # Break after end of block, unless it's the last block.
            # Experimenter can re-calibrate the eyetracker by pressing 'c' here.
            calibrated = True
            if block_nr + 1 == N_BLOCKS // 2:
                while calibrated:
                    calibrated = long_break(
                        N_BLOCKS,
                        avg_score,
                        settings,
                        eyetracker=None if testing else eyelinker,
                    )
                if not testing:
                    eyelinker.start()
            elif block_nr + 1 < N_BLOCKS:
                while calibrated:
                    calibrated = block_break(
                        block_nr + 1,
                        N_BLOCKS,
                        avg_score,
                        settings,
                        eyetracker=None if testing else eyelinker,
                    )

            # Make sure the keystroke from continueing to the next block isn't saved
            settings["keyboard"].clearEvents()

        finished_early = False

    except Exception as e:
        if not isinstance(e, KeyboardInterrupt):
            print(e)
            print(traceback.format_exc())

    finally:
        # Stop eyetracker (this should also save the data)
        if not testing:
            eyelinker.stop()

        # Save all collected trial data to a new .csv
        pd.DataFrame(data).to_csv(
            rf"{settings['directory']}\data_session_{new_participants.session_number.iloc[-1]}_{current_block_type}{'_test' if testing else ''}.csv",
            index=False,
        )

        # Register how many trials this participant has completed
        new_participants.loc[new_participants.index[-1], "trials_completed"] = str(
            len(data)
        )

        # Save participant data to existing .csv file
        new_participants.to_csv(
            rf"{settings['directory']}\participantinfo.csv", index=False
        )

        # Done!
        if finished_early:
            quick_finish(settings)
        else:
            # Thanks for meedoen
            finish(N_BLOCKS, settings)

        core.quit()


if __name__ == "__main__":
    main()
