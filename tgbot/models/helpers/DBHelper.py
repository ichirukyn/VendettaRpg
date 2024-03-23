import logging
import os
from datetime import datetime


class DatabaseHelper:
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'database_helper.log')

    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(message)s')
    logger = logging.getLogger(__name__)

    def init_bd(self, *args: dict, default_value=0, logger=None):
        for data_dict in args:
            old_values = {key: getattr(self, key, default_value) for key in data_dict.keys()}

            for key, value in data_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    if logger is not None:
                        self.logger.warning(f"Поле {key} не найдено в классе. Используется значение по умолчанию.")

                    setattr(self, key, default_value)

            new_values = {key: getattr(self, key, default_value) for key in data_dict.keys()}
            self.log_changes(old_values, new_values)

    def log_changes(self, old_values, new_values):
        if self.logger:
            self.logger.info(
                f"[{datetime.now().strftime('%d.%m.%y - %H:%M')}] "
                f"LOG Init-db:\n------\nКласс: {self.__class__.__name__}()"
            )
            self.logger.info("Прошлые свойства:")

            for key, value in old_values.items():
                self.logger.info(f"{key} = {value}")

            self.logger.info("\nНовые свойства:")

            for key, value in new_values.items():
                self.logger.info(f"{key} = {value}")

            self.logger.info("------\n\n")
