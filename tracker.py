class LineCounter:
    """
    Tracks vehicles crossing two horizontal lines.

    ENTRY : vehicle moves top  -> bottom across entry_line_y
    EXIT  : vehicle moves bottom -> top  across exit_line_y

    A track_id can trigger ENTRY once and EXIT once.
    """

    def __init__(self, entry_line_y, exit_line_y=None):

        # If no exit line is given, place it above the entry line
        # as a sensible default (vehicles exit the way they came).
        self.entry_line_y = entry_line_y
        self.exit_line_y = exit_line_y if exit_line_y is not None else entry_line_y - 50

        self.previous_positions = {}

        # Sets to ensure each event fires only once per track_id
        self.entered = set()
        self.exited  = set()

    def check_crossing(self, track_id, center_y):
        """
        Returns "ENTRY", "EXIT", or None.
        """

        if track_id not in self.previous_positions:
            self.previous_positions[track_id] = center_y
            return None

        previous_y = self.previous_positions[track_id]
        self.previous_positions[track_id] = center_y

        # ---- ENTRY: top -> bottom across entry line ----
        if (
            track_id not in self.entered
            and previous_y < self.entry_line_y
            and center_y >= self.entry_line_y
        ):
            self.entered.add(track_id)
            return "ENTRY"

        # ---- EXIT: bottom -> top across exit line ----
        # Only fire for vehicles that already entered.
        if (
            track_id in self.entered
            and track_id not in self.exited
            and previous_y > self.exit_line_y
            and center_y <= self.exit_line_y
        ):
            self.exited.add(track_id)
            return "EXIT"

        return None
