from typing import Callable, Optional
from ..map import Position, PositionType
from ..aircraft import Aircraft
from ..utils.logger import logger


class Airport(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
        /,
        special_condition: Optional[Callable[["Position", Aircraft], bool]] = None,
    ):
        super().__init__(
            name,
            longitude,
            latitude,
            helicopter_area,
            fixed_area,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            special_condition=special_condition,
        )

        logger.info(f"创建机场 {name}")


class DisasterArea(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
        air_work_area: float,
        supply: int,
        rescue_people: int,
        trapped_people: int,
        device: int,
        patient: int,
        water: int,
        /,
        search: tuple[bool, float] = (False, 0),
        p_type: PositionType = "Land",
        special_condition: Optional[Callable[[Position, Aircraft], bool]] = None,
    ) -> None:
        super().__init__(
            name,
            longitude,
            latitude,
            helicopter_area,
            fixed_area,
            air_work_area,
            0,
            0,
            trapped_people,
            0,
            patient,
            0,
            p_type=p_type,
            special_condition=special_condition,
        )

        self.need_supply: int = supply
        self.need_water: int = water
        self.need_rescue_people: int = rescue_people
        self.need_device: int = device
        self.search: tuple[bool, float] = search
        self.already_search: float = 0

        logger.info(f"创建灾区 {name}")

    @property
    def need_search(self) -> bool:
        return self.search[0]

    @property
    def is_search_done(self) -> bool:
        return self.already_search >= self.search[1]


class Hospital(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
        /,
        special_condition: Optional[Callable[["Position", Aircraft], bool]] = None,
    ):
        super().__init__(
            name,
            longitude,
            latitude,
            helicopter_area,
            fixed_area,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            special_condition=special_condition,
        )

        logger.info(f"创建医院 {name}")


class NormalArea(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
        air_work_area: float,
        supply: int,
        rescue_people: int,
        trapped_people: int,
        device: int,
        patient: int,
        water: int,
        /,
        special_condition: Optional[Callable[["Position", Aircraft], bool]] = None,
    ) -> None:
        super().__init__(
            name,
            longitude,
            latitude,
            helicopter_area,
            fixed_area,
            air_work_area,
            supply,
            rescue_people,
            trapped_people,
            device,
            patient,
            water,
            special_condition=special_condition,
        )

        logger.info(f"创建地点 {name}")


class Source(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
        air_work_area: float,
        supply: int,
        rescue_people: int,
        device: int,
        water: int,
        /,
        special_condition: Optional[Callable[["Position", Aircraft], bool]] = None,
    ) -> None:
        super().__init__(
            name,
            longitude,
            latitude,
            helicopter_area,
            fixed_area,
            air_work_area,
            supply,
            rescue_people,
            0,
            device,
            0,
            water,
            special_condition=special_condition,
        )

        logger.info(f"创建地点 {name}")


class Destination(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
        air_work_area: float,
        /,
        special_condition: Optional[Callable[["Position", Aircraft], bool]] = None,
    ) -> None:
        super().__init__(
            name,
            longitude,
            latitude,
            helicopter_area,
            fixed_area,
            air_work_area,
            0,
            0,
            0,
            0,
            0,
            0,
            special_condition=special_condition,
        )

        logger.info(f"创建地点 {name}")
