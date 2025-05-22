import sys
import datetime

class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

class Logger:
    def __init__(self, use_colors=True, Debug = True, stream=sys.stdout):
        self.use_colors = use_colors
        self.stream = stream
        self.Debug = Debug

    def _color(self, text, color_code):
        if self.use_colors:
            return f"{color_code}{text}{LogColors.ENDC}"
        return text

    def _log(self, level, message, color):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_str = self._color(f"[{level}]", color)
        print(f"{timestamp} {level_str} {message}", file=self.stream)

    def info(self, message):
        if not self.Debug:
            return
        self._log("INFO", message, LogColors.OKGREEN)

    def warning(self, message):
        if not self.Debug:
            return
        self._log("WARNING", message, LogColors.WARNING)

    def error(self, message):
        if not self.Debug:
            return
        self._log("ERROR", message, LogColors.FAIL)
