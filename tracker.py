class LineCounter:

    def __init__(self, line_y):

        self.line_y = line_y

        self.previous_positions = {}

        self.crossed = set()

    def check_crossing(self, track_id, center_y):

        if track_id not in self.previous_positions:

            self.previous_positions[track_id] = center_y
            return None

        previous_y = self.previous_positions[track_id]

        self.previous_positions[track_id] = center_y

        if track_id in self.crossed:
            return None

        if previous_y < self.line_y and center_y >= self.line_y:

            self.crossed.add(track_id)

            return "ENTRY"

        return None