"""
This file contains the functions necessary for
collecting participant data.
To run the 'microsaccade bias duration' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

import random
import pandas as pd

BLOCK_OPTIONS = ["auditory", "visual"]


def get_participant_details(existing_participants: pd.DataFrame, testing):
    # Determine if this is first or second session of pp
    pp_id_list = existing_participants.participant_number.tolist()

    if len(pp_id_list) == 1 or pp_id_list[-1] == pp_id_list[-2]:
        # This must be this participant's first session
        current_session = 1

        # Generate random & unique participant number
        participant = random.randint(10, 99)
        while participant in existing_participants.participant_number.tolist():
            participant = random.randint(10, 99)

        # Get participant age if not a trial-run
        if not testing:
            age = int(input("Participant age: "))
        else:
            age = 00

        # Determine starting block type

        previous_start_block_type = existing_participants.start_block_type.tolist()[-1]
        if previous_start_block_type == "0":
            start_block_type = BLOCK_OPTIONS[0]
        else:
            idx = (BLOCK_OPTIONS.index(previous_start_block_type) + 1) % len(
                BLOCK_OPTIONS
            )
            start_block_type = BLOCK_OPTIONS[idx]

        # Insert session number
        session = max(existing_participants.session_number) + 1

    else:
        current_session = 2
        participant = pp_id_list[-1]
        age = existing_participants.age.tolist()[-1]
        start_block_type = existing_participants.start_block_type.tolist()[-1]
        session = max(existing_participants.session_number)

    # Determine current block type
    current_block = (
        start_block_type
        if current_session == 1
        else BLOCK_OPTIONS[
            (BLOCK_OPTIONS.index(start_block_type) + 1) % len(BLOCK_OPTIONS)
        ]
    )

    # Print relevant information
    print(f"Session  {current_session}  for participant number: {participant}")
    print(f"Block type: {current_block}")

    # Add newly made participant
    new_participant = pd.DataFrame(
        {
            "participant_number": [participant],
            "session_number": [session],
            "session_within_pp": [current_session],
            "age": [age],
            "start_block_type": [start_block_type],
            "current_block_type": [current_block],
        }
    )
    all_participants = pd.concat(
        [existing_participants, new_participant], ignore_index=True
    )

    # Break before return so experimenter has a chance to show the instruction powerpoint
    input("Instruction powerpoint shown? (y/n)  ")

    return all_participants, current_block
