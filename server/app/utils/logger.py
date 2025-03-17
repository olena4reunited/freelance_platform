import logging


class LoggerFormatter(logging.Formatter):
    COLORS = {
        "CRITICAL": "\x1b[1;31m",
        "WARNING": "\x1b[33m",
        "ERROR": "\x1b[31m",
        "DEBUG": "\x1b[33m",
        "INFO": "\x1b[32m",
    }

    reset = "\x1b[0m"

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, self.reset)
        padding = " " * (9 - len(record.levelname))
        levelname_padded = f"{record.levelname}{self.reset}:{padding}"
        
        logmessage_formatted = f"{level_color}{levelname_padded}{record.msg}"
    
        record.msg = logmessage_formatted
        return super().format(record)


logger = logging.getLogger("server")

logger.setLevel(logging.DEBUG)  

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

handler.setFormatter(LoggerFormatter())

logger.addHandler(handler)
