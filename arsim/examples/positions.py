from typing import Callable, Optional
from ..map import Position, PositionType
from ..aircraft import Aircraft


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
