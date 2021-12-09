"""Модуль фитнес-трекера для расчёта и отображения информации
о прошедшей тренировке по данным от блока датчиков."""

from typing import Sequence, ClassVar
from dataclasses import dataclass, fields

MIN_IN_H = 60
UNKNOWN_WORKOUT_TYPE_ERROR_TEMPLATE = "Неизвестный тип тренировки: {}"
WRONG_PACKAGE_SIZE_ERROR_TEMPLATE = (
    "Получен пакет размера {actual_size}. "
    "Для тренировки типа {workout_type} "
    "ожидается пакет размера {expected_size}."
)


@dataclass
class InfoMessage:

    """Информационное сообщение о тренировке."""

    INFO_MESSAGE_TEMPLATE: ClassVar[str] = (
        'Тип тренировки: {training_type}; '
        'Длительность: {duration:.3f} ч.; '
        'Дистанция: {distance:.3f} км; '
        'Ср. скорость: {speed:.3f} км/ч; '
        'Потрачено ккал: {calories:.3f}.'
    )

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float

    def get_message(self) -> str:
        """Возвращает строку с информационным сообщением о тренировке."""
        return self.INFO_MESSAGE_TEMPLATE.format(
            training_type=self.training_type,
            duration=self.duration,
            distance=self.distance,
            speed=self.speed,
            calories=self.calories,
        )


@dataclass
class Training:

    """Базовый класс тренировки."""

    M_IN_KM: ClassVar[int] = 1000
    LEN_STEP: ClassVar[float] = 0.65

    action: int
    duration: float
    weight: float

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return self.get_distance() / self.duration

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        pass

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(
            self.__class__.__name__,
            self.duration,
            self.get_distance(),
            self.get_mean_speed(),
            self.get_spent_calories(),
        )

    @property
    def duration_minutes(self) -> float:
        """Длительность тренировки в минутах"""
        return self.duration * MIN_IN_H


@dataclass
class Running(Training):

    """Тренировка: бег."""

    MEAN_SPEED_FACTOR: ClassVar[int] = 18
    MEAN_SPEED_SUBTRAHEND: ClassVar[int] = 20

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        speed = self.get_mean_speed()
        return (
            (self.MEAN_SPEED_FACTOR * speed - self.MEAN_SPEED_SUBTRAHEND)
            * self.weight
            / self.M_IN_KM
            * self.duration_minutes
        )


@dataclass
class SportsWalking(Training):

    """Тренировка: спортивная ходьба."""

    WEIGHT_FACTOR_1: ClassVar[float] = 0.035
    WEIGHT_FACTOR_2: ClassVar[float] = 0.029

    height: float

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        speed = self.get_mean_speed()
        return self.duration_minutes * (
            self.WEIGHT_FACTOR_1 * self.weight
            + (speed ** 2 // self.height) * self.WEIGHT_FACTOR_2 * self.weight
        )


@dataclass
class Swimming(Training):

    """Тренировка: плавание."""

    LEN_STEP: ClassVar[float] = 1.38
    MEAN_SPEED_TERM: ClassVar[float] = 1.1
    WEIGHT_FACTOR: ClassVar[int] = 2

    length_pool: float
    count_pool: int

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
        return (
            (self.get_mean_speed() + self.MEAN_SPEED_TERM)
            * self.WEIGHT_FACTOR
            * self.weight
        )


class PackageValidationError(Exception):
    """Базовый класс ошибок валидации пакетов."""
    pass


class PackageTypeError(PackageValidationError):
    """Неизвестный тип тренировки в пакете."""
    pass


class PackageSizeError(PackageValidationError):
    """Размер пакета не соответствует ожидаемому."""
    pass


TRAINING_CLASSES = {
    'WLK': SportsWalking,
    'RUN': Running,
    'SWM': Swimming
}


def read_package(workout_type: str, data: Sequence[float]) -> Training:
    """Прочитать данные полученные от датчиков."""
    class_ = TRAINING_CLASSES.get(workout_type)
    if class_ is None:
        raise PackageTypeError(
            UNKNOWN_WORKOUT_TYPE_ERROR_TEMPLATE.format(workout_type)
        )

    actual_package_size = len(data)
    expected_package_size = len(fields(class_))
    if actual_package_size != expected_package_size:
        raise PackageSizeError(
            WRONG_PACKAGE_SIZE_ERROR_TEMPLATE.format(
                actual_size=actual_package_size,
                expected_size=expected_package_size,
                workout_type=workout_type
            )
        )

    return class_(*data)


def main(training: Training) -> None:
    """Главная функция."""
    print(training.show_training_info().get_message())


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
        ('WLK', [9000, 1, 75, 180, 11]),
        ('BIC', [9000, 1])
    ]

    for workout_type, data in packages:
        try:
            main(read_package(workout_type, data))
        except PackageValidationError as e:
            print(e)
