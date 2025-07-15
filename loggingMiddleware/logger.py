import datetime
import os


class FileLogger:
    def __init__(self, log_file="loggingMiddleware/logs/app.log"):  # Use forward slashes
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.log_file = log_file

    def _write_log(self, stack: str, level: str, package: str, message: str):
        timestamp = datetime.datetime.now().isoformat()
        log_line = f"[{timestamp}] [STACK: {stack}] [LEVEL: {level.upper()}] [PACKAGE: {package}] MESSAGE: {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_line)

    def log(self, stack: str, level: str, package: str, message: str):
        valid_stacks = {"frontend", "backend"}
        valid_levels = {"debug", "info", "warn", "error", "fatal"}
        valid_packages = {"cache", "controller", "cron_job", "db", "domain", "handler", "repository", "route", "service"}

        if stack not in valid_stacks:
            raise ValueError(f"Invalid stack value: {stack}. Allowed values are: {valid_stacks}")
        if level not in valid_levels:
            raise ValueError(f"Invalid level value: {level}. Allowed values are: {valid_levels}")
        if package not in valid_packages:
            raise ValueError(f"Invalid package value: {package}. Allowed values are: {valid_packages}")

        self._write_log(stack, level, package, message)





