from ..map import Position


class Airport(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
    ):
        super().__init__(
            name, longitude, latitude, helicopter_area, fixed_area, 0, 0, 0, 0, 0, 0, 0
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
        )


class Hospital(Position):
    def __init__(
        self,
        name: str,
        longitude: float,
        latitude: float,
        helicopter_area: float,
        fixed_area: float,
    ):
        super().__init__(
            name, longitude, latitude, helicopter_area, fixed_area, 0, 0, 0, 0, 0, 0, 0
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
        )
