"""Модуль фитнес-трекера для расчёта и отображения информации
о прошедшей тренировке по данным от блока датчиков."""

from typing import Sequence


class InfoMessage:
    """Информационное сообщение о тренировке."""

    def __init__(self,
                 training_type: str,
                 duration: float,
                 distance: float,
                 speed: float,
                 calories: float) -> None:
        self.training_type = training_type
        self.duration = duration
        self.distance = distance
        self.speed = speed
        self.calories = calories

    def as_string(self) -> str:
        """Возвращает строку с информационным сообщением о тренировке."""
        return (f'Тип тренировки: {self.training_type}; '
                f'Длительность: {self.duration:.3f} ч.; '
                f'Дистанция: {self.distance:.3f} км; '
                f'Ср. скорость: {self.speed:.3f} км/ч; '
                f'Потрачено ккал: {self.calories:.3f}.')


class Training:
    """Базовый класс тренировки."""

    M_IN_KM = 1000
    LEN_STEP = 0.65

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 ) -> None:
        self.action = action
        self.duration = duration
        self.weight = weight

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        distance = self.get_distance()
        return distance / self.duration

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        pass

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__,
                           self.duration,
                           self.get_distance(),
                           self.get_mean_speed(),
                           self.get_spent_calories(),
                           )

    @property
    def duration_minutes(self) -> float:
        """Длительность тренировки в минутах"""
        min_in_h = 60
        return self.duration * min_in_h


class Running(Training):
    """Тренировка: бег."""
    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        coeff_1 = 18
        coeff_2 = 20
        speed = self.get_mean_speed()
        calories = (
                (coeff_1 * speed - coeff_2)
                * self.weight
                / self.M_IN_KM
                * self.duration_minutes
        )
        return calories


class SportsWalking(Training):
    """Тренировка: спортивная ходьба."""

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 height: float,
                 ) -> None:
        super().__init__(action, duration, weight)
        self.height = height

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        coeff_1 = 0.035
        coeff_2 = 2
        coeff_3 = 0.029
        speed = self.get_mean_speed()
        calories = self.duration_minutes * (
                coeff_1 * self.weight
                + (speed ** coeff_2 // self.height) * coeff_3 * self.weight
        )
        return calories


class Swimming(Training):
    """Тренировка: плавание."""

    LEN_STEP = 1.38

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 length_pool: float,
                 count_pool: float,
                 ) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool
        self.count_pool = count_pool

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return (
            self.length_pool
            * self.count_pool
            / self.M_IN_KM
            / self.duration
        )

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        coeff_1 = 1.1
        coeff_2 = 2
        speed = self.get_mean_speed()
        return (speed + coeff_1) * coeff_2 * self.weight


def read_package(workout_type: str, data: Sequence[float]) -> Training:
    """Прочитать данные полученные от датчиков."""
    training_classes_mapping = {
        'WLK': SportsWalking,
        'RUN': Running,
        'SWM': Swimming
    }
    class_ = training_classes_mapping[workout_type]
    return class_(*data)


def main(training: Training) -> None:
    """Главная функция."""
    info = training.show_training_info()
    print(info.as_string())


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        main(training)
