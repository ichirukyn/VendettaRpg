import glob
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


class SimulationLogger:
    def __init__(self, directory, file_pattern, log_name, max_files=10):
        self.directory = directory
        self.file_pattern = file_pattern
        self.max_files = max_files

        # Настройка базового конфига логгера
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(log_name)

        # Получаем текущее время для создания уникального имени файла
        current_time = datetime.now().strftime("%d-%H-%M")
        log_filename = f"{self.directory}/{log_name}_{current_time}.log"

        # Добавление обработчика файла, который будет записывать логи в файл с уникальным именем
        handler = RotatingFileHandler(log_filename, maxBytes=5000000, backupCount=5, encoding='utf-8')
        self.logger.addHandler(handler)

    # Функция для очистки старых лог-файлов
    def cleanup_logs(self):
        files = sorted(glob.glob(os.path.join(self.directory, self.file_pattern)), key=os.path.getmtime)
        while len(files) > self.max_files:
            os.remove(files.pop(0))
