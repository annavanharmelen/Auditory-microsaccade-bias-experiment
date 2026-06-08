"""
This file contains the functions necessary for
connecting and using the eyetracker.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025, using code by Ezra Nasrawi & Baiwei Liu
"""

from lib import eyelinker
from psychopy import event
import os


class Eyelinker:
    """
    usage:

       from eyetracker import Eyelinker

    To initialise:

       eyelinker = Eyelinker(participant, session, window, directory)
       eyelinker.calibrate()
    """

    def __init__(self, participant, session, block_type_id, window, directory) -> None:
        """
        This also connects to the tracker
        """
        self.directory = directory
        self.window = window
        self.tracker = eyelinker.EyeLinker(
            window=window,
            eye="RIGHT",
            filename=f"{session}_{participant}_{block_type_id}.edf",
        )
        self.tracker.init_tracker()

    def start(self):
        self.tracker.start_recording()

    def calibrate(self):
        self.tracker.calibrate()

    def stop(self):
        os.chdir(self.directory)

        self.tracker.stop_recording()
        self.tracker.transfer_edf()
        self.tracker.close_edf()


def get_trigger(frame, target_item, task_type, target_position):
    condition_marker = int(target_item)

    if task_type == "visual":
        condition_marker += 4

    if target_position == "right":
        condition_marker += 2

    return {
        "stimulus_onset_1": "1",
        "stimulus_onset_2": "2",
        "cue_onset": "3",
        "response_onset": "4",
        "response_offset": "5",
        "feedback_onset": "6",
    }[frame] + str(condition_marker)
