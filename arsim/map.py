from typing import Literal, Optional, Union, Callable
import math
from .aircraft import Aircraft
from .utils.logger import logger

DistanceCalculateMethod = Literal["Flat"] | Literal["Vincenty"] | Literal["Haversine"]
PositionType = Literal["Sea"] | Literal["Land"]


class FailConvertException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Map:
    def __init__(self, *pos: "Position") -> None:
        self.position: list[Position] = list(pos)
        self.map: dict[str, Union[Position, tuple[Position, ...]]] = {}

        for p in pos:
            if p.name in self.map:
                ref = self.map[p.name]
                if isinstance(ref, Position):
                    self.map[p.name] = (ref, p)
                else:
                    self.map[p.name] = ref + (p,)
            else:
                self.map[p.name] = p
        
        logger.info(f"地图初始化完成，共有 {len(self.position)} 个地点")

    def __getitem__(self, index: str) -> tuple["Position", ...]:
        if index in self.map:
            ref = self.map[index]
            if isinstance(ref, Position):
                return (ref,)
            else:
                return ref
        else:
            return ()


class Position:
    _distance_method: DistanceCalculateMethod = "Vincenty"

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
        p_type: PositionType = "Land",
        special_condition: Optional[Callable[["Position", Aircraft], bool]] = None,
    ) -> None:
        # 地点名称
        self.name: str = name

        # 经度（负为西）
        self.longitude: float = longitude
        # 纬度（负为南）
        self.latitude: float = latitude

        # 基础信息
        # 直升机可降落面积
        self.helicopter_area: float = helicopter_area
        # 固定翼飞机可降落面积
        self.fixed_area: float = fixed_area
        # 当前空中作业面积，超出面积则无法作业
        self.air_work_area: float = air_work_area

        # 可提供资源
        # 可提供救援物资量
        self.supply: int = supply
        # 可提供的救援人员数量
        self.rescue_people: int = rescue_people
        # 现有受困群众数量
        self.trapped_people: int = trapped_people
        # 现有重型救灾装备数量
        self.device: int = device
        # 现有重病患者数量
        self.patient: int = patient
        # 当前地点可提供的水量
        self.water: int = water

        # 地点的位置
        self.type: PositionType = p_type
        # 特殊需求
        self.special_condition: Optional[
            Callable[["Position", Aircraft], bool]
        ] = special_condition

    @staticmethod
    def distance(
        p1: "Position", p2: "Position", method: Optional[DistanceCalculateMethod] = None
    ) -> float:
        """
        计算两个地点之间的距离（km）
        """
        if method is None:
            method = Position._distance_method

        if method == "Flat":
            return Position._distance_flat(p1, p2)
        elif method == "Vincenty":
            return Position._distance_vincenty(p1, p2) / 1000
        elif method == "Haversine":
            return Position._distance_haversine(p1, p2)

    @staticmethod
    def _distance_flat(p1: "Position", p2: "Position") -> float:
        return math.sqrt(
            ((p1.longitude - p2.longitude) * 111) ** 2
            + ((p1.latitude - p2.latitude) * 111) ** 2
        )

    @staticmethod
    def _distance_vincenty(
        p1: "Position", p2: "Position", circleCount: int = 40
    ) -> float:
        """
        计算两个位置间的距离（m）
        https:#en.wikipedia.org/wiki/Vincenty%27s_formulae
        """
        a = 6378137.0
        b = 6356752.314245
        f = 1 / 298.257223563

        L = math.radians(p1.longitude) - math.radians(p2.longitude)
        U1 = math.atan((1 - f) * math.tan(math.radians(p1.latitude)))
        U2 = math.atan((1 - f) * math.tan(math.radians(p2.latitude)))
        sinU1, cosU1 = math.sin(U1), math.cos(U1)
        sinU2, cosU2 = math.sin(U2), math.cos(U2)
        lam, lamP = L, math.pi
        cosSqAlpha: float = 0
        sinSigma: float = 0
        cos2SigmaM: float = 0
        cosSigma: float = 0
        sigma: float = 0

        # 迭代循环
        while abs(lam - lamP) > 1e-12 and circleCount > 0:
            sinLam, cosLam = math.sin(lam), math.cos(lam)
            sinSigma = math.sqrt(
                (cosU2 * sinLam) * (cosU2 * sinLam)
                + (cosU1 * sinU2 - sinU1 * cosU2 * cosLam)
                * (cosU1 * sinU2 - sinU1 * cosU2 * cosLam)
            )
            if sinSigma == 0:
                return 0
            cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLam
            sigma = math.atan2(sinSigma, cosSigma)
            alpha = math.asin(cosU1 * cosU2 * sinLam / sinSigma)
            cosSqAlpha = math.cos(alpha) * math.cos(alpha)
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
            C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
            lamP = lam
            lam = L + (1 - C) * f * math.sin(alpha) * (
                sigma
                + C
                * sinSigma
                * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM))
            )
            circleCount -= 1

        if circleCount == 0:
            raise FailConvertException("未能成功转化为距离")

        uSq = cosSqAlpha * (a * a - b * b) / (b * b)
        A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
        B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
        deltaSigma = (
            B
            * sinSigma
            * (
                cos2SigmaM
                + B
                / 4
                * (
                    cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)
                    - B
                    / 6
                    * cos2SigmaM
                    * (-3 + 4 * sinSigma * sinSigma)
                    * (-3 + 4 * cos2SigmaM * cos2SigmaM)
                )
            )
        )

        result = b * A * (sigma - deltaSigma)
        return result

    @staticmethod
    def _distance_haversine(p1: "Position", p2: "Position") -> float:
        lng1 = math.radians(p1.longitude)
        lat1 = math.radians(p1.latitude)
        lng2 = math.radians(p2.longitude)
        lat2 = math.radians(p2.latitude)

        a = lat1 - lat2
        b = lng1 - lng2

        return (
            2
            * math.asin(
                math.sqrt(
                    math.sin(a / 2) * math.sin(a / 2)
                    + math.cos(lat1)
                    * math.cos(lat2)
                    * math.sin(b / 2)
                    * math.sin(b / 2)
                )
            )
            * 6378.137
        )
