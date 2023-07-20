from typing import Literal, Any, TypedDict, Unpack, NotRequired, Callable, Optional
from math import isclose
from .scene import Scene
from .aircraft import Aircraft
from .map import Position
from .examples import positions as mpos

# pyright: reportTypedDictNotRequiredAccess = false

TaskType = (
    Literal["装载"]
    | Literal["卸货"]
    | Literal["运送"]
    | Literal["投放"]
    | Literal["绞车投放"]
    | Literal["吊运"]
    | Literal["卸载"]
    | Literal["转移"]
    | Literal["绞车转移"]
    | Literal["安置"]
    | Literal["转运"]
    | Literal["绞车转运"]
    | Literal["交接"]
    | Literal["取水"]
    | Literal["灭火"]
    | Literal["侦查搜寻"]
    | Literal["加油保障"]
)


class UnsupportedSubtaskException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MissingSubtaskInformationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PositionNotSupportedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SubTaskSucceedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SpecialConditionNotSatisfiedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PositionNotExistException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotSupportedTaskException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SubTaskParams(TypedDict):
    # 装载物资的数量
    load_supply: NotRequired[int]
    # 卸载物资的数量
    # unload_supply: NotRequired[int]
    # 运送人员数量
    load_people: NotRequired[int]
    # 投放人员数量
    # unload_people: NotRequired[int]
    # 绞车投放人员数量
    # unload_winch_people: NotRequired[int]
    # 吊运设备数量
    load_device: NotRequired[int]
    # 卸载设备数量
    # unload_device: NotRequired[int]
    # 转移灾民数量
    load_refugee: NotRequired[int]
    # # 绞车转移灾民数量
    # load_winch_refugee: NotRequired[int]
    # 安置灾民数量
    # unload_refugee: NotRequired[int]
    # 转运伤患数量
    load_patient: NotRequired[int]
    # # 绞车转运伤患数量
    # load_winch_patient: NotRequired[int]
    # 交接伤患数量
    # unload_patient: NotRequired[int]
    # 取水数量
    load_water: NotRequired[int]
    # 灭火用水数量
    # unload_water: NotRequired[int]


class SubTask:
    _LAND_SUBTASK: list[TaskType] = [
        "装载",
        "卸货",
        "运送",
        "投放",
        "转移",
        "安置",
        "转运",
        "交接",
        "加油保障",
    ]
    _AIR_SUBTASK: list[TaskType] = [
        "绞车投放",
        "吊运",
        "卸载",
        "绞车转移",
        "绞车转运",
        "取水",
        "灭火",
        "侦查搜寻",
    ]

    def __init__(
        self,
        scene: Scene,
        task_type: TaskType,
        aircraft: Aircraft,
        position: Position,
        **kwargs: Unpack[SubTaskParams],
    ) -> None:
        # 所属推演场景
        self.scene: Scene = scene
        # 所属子任务类型
        self.type: TaskType = task_type
        # 执行任务的航空器
        self.aircraft: Aircraft = aircraft
        # 执行任务的地点
        self.position: Position = position
        # 任务附加信息
        self.addition: SubTaskParams = kwargs
        # 是否已经加油保障
        self.is_fueled: bool = False

        if self.position not in self.scene.map.position:
            raise PositionNotExistException(f"地点 {self.position.name} 不存在")

        if not self.check_aircraft_valid():
            raise UnsupportedSubtaskException(
                f"航空器 {self.aircraft.name} 不能执行 {self.type} 任务"
            )

        if not self.check_position_valid():
            raise UnsupportedSubtaskException(
                f"航空器 {self.aircraft.name} 在地点 {self.position.name} 不能执行 {self.type} 任务"
            )

    def setup(self) -> None:
        """子任务初始化
        """
        # 移动初始化
        if self.aircraft.now_position is not None:
            # 航空器移动距离
            self.distance: float = Position.distance(
                self.aircraft.now_position, self.position
            )
            self.move_process: float = 0
        else:
            raise

        # 任务初始化
        self.task_process: float = 0

    @property
    def is_arrived(self) -> bool:
        """
        航空器是否移动到目的地
        """
        return (
            isclose(self.move_process, 1)
            and self.aircraft.now_position == self.position
        )

    @property
    def is_finished(self) -> bool:
        """
        航空器是否完成该子任务
        """
        return isclose(self.task_process, 1)

    @property
    def consume_time_raw(self) -> float:
        """任务总共消耗时间（秒）

        Raises:
            UnsupportedSubtaskException: 不支持的子任务类型

        Returns:
            float: 需要的时间
        """
        c_time: float = 0
        if self.type == "加油保障":
            if isinstance(self.aircraft.now_position, mpos.Aircraft):
                c_time = self.aircraft.fuel_fill_time
            else:
                c_time = 0
        elif self.type == "装载":
            c_time = self.aircraft.supply_load_time * self.addition["load_supply"]
        elif self.type == "卸货":
            c_time = self.aircraft.supply_load_time * self.aircraft.now_supply
        elif self.type == "运送":
            c_time = self.aircraft.person_on_off_time * self.addition["load_people"]
        elif self.type == "投放":
            c_time = self.aircraft.person_on_off_time * self.aircraft.now_resuce_people
        elif self.type == "绞车投放":
            c_time = self.aircraft.winch_person_time * self.aircraft.now_resuce_people
        elif self.type == "吊运" or self.type == "卸载":
            c_time = self.aircraft.device_load_time
        elif self.type == "转移":
            c_time = self.aircraft.person_on_off_time * self.addition["load_refugee"]
        elif self.type == "绞车转移":
            c_time = self.aircraft.winch_person_time * self.addition["load_refugee"]
        elif self.type == "安置":
            c_time = self.aircraft.person_on_off_time * self.aircraft.now_trapped_people
        elif self.type == "转运":
            c_time = self.aircraft.patient_on_off_time * self.addition["load_patient"]
        elif self.type == "绞车转运":
            c_time = self.aircraft.winch_patient_time * self.addition["load_patient"]
        elif self.type == "交接":
            c_time = self.aircraft.patient_on_off_time * self.aircraft.now_ill_people
        elif self.type == "取水":
            c_time = (
                self.aircraft.water_load_time
                / self.aircraft.max_external_load
                * self.addition["load_water"]
            )
        elif self.type == "灭火":
            c_time = (
                self.aircraft.extinguishing_time
                / self.aircraft.max_external_load
                * self.aircraft.now_water
            )
        elif self.type == "侦查搜寻":
            tmp: mpos.DisasterArea = self.position  # type: ignore
            c_time = self.aircraft.search_time * (tmp.search[1] - tmp.already_search)
        else:
            raise UnsupportedSubtaskException(f"不支持的子任务类型 {self.type}")
        return c_time

    @property
    def consume_time(self) -> float:
        """
        任务还需要进行的时间 (单位：秒)
        """

        return self.consume_time_raw * (1 - self.task_process)

    @property
    def move_time(self) -> float:
        """
        飞机移动时间 (单位：秒)
        """
        return self.distance * (1 - self.move_process) / self.aircraft.cruising_speed

    def check_aircraft_valid(self) -> bool:
        """
        检验所指派的航空器能否执行该任务
        """
        # 侦查
        if self.type == "侦查搜寻":
            if not self.aircraft.ability.can("Reconnoitre"):
                return False
        # 消防
        elif self.type == "取水":
            if not self.aircraft.ability.can("Fire"):
                return False
            if "load_water" not in self.addition:
                raise MissingSubtaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_water 信息"
                )
            if (
                self.addition["load_water"] + self.aircraft.now_external
                > self.aircraft.max_external_load
            ):
                raise UnsupportedSubtaskException(
                    f'航空器 {self.aircraft.name} 无法取水 {self.addition["load_water"]} 吨'
                )
        elif self.type == "灭火":
            if not self.aircraft.ability.can("Fire"):
                return False
            if self.aircraft.now_water <= 0:
                raise UnsupportedSubtaskException(f"航空器 {self.aircraft.name} 上没有多余的水")
        # 货运
        elif self.type == "装载":
            if not self.aircraft.ability.can("Freight"):
                return False
            if "load_supply" not in self.addition:
                raise MissingSubtaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_supply 信息"
                )
            if (
                self.addition["load_supply"] + self.aircraft.now_internal
                > self.aircraft.max_internal_load
            ):
                raise UnsupportedSubtaskException(
                    f'航空器 {self.aircraft.name} 无法装载救援物资 {self.addition["load_supply"]} 千克'
                )
        elif self.type == "卸货":
            if not self.aircraft.ability.can("Freight"):
                return False
            if self.aircraft.now_supply <= 0:
                raise UnsupportedSubtaskException(f"航空器 {self.aircraft.name} 上没有装载的物资")
        # 载人
        elif self.type == "运送":
            if not self.aircraft.ability.can("Manned"):
                return False
            if "load_people" not in self.addition:
                raise MissingSubtaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_people 信息"
                )
            if (
                self.aircraft.now_people + self.addition["load_people"]
                > self.aircraft.max_capacity
            ):
                raise UnsupportedSubtaskException(
                    f'航空器 {self.aircraft.name} 无法运送人员 {self.addition["load_people"]} 人'
                )
        elif self.type == "投放":
            if not self.aircraft.ability.can("Manned"):
                return False
            if self.aircraft.now_resuce_people <= 0:
                raise UnsupportedSubtaskException(f"航空器 {self.aircraft.name} 上没有救援人员")
        elif self.type == "绞车投放":
            if not self.aircraft.ability.can("Manned", "Winch"):
                return False
            if self.aircraft.now_resuce_people <= 0:
                raise UnsupportedSubtaskException(f"航空器 {self.aircraft.name} 上没有救援人员")
        # 吊挂
        elif self.type == "吊运":
            if not self.aircraft.ability.can("Hanging"):
                return False
            if self.aircraft.now_external + 10_000 > self.aircraft.max_external_load:
                raise UnsupportedSubtaskException(
                    f"航空器 {self.aircraft.name} 无法吊运 10 吨的设备"
                )
        elif self.type == "卸载":
            if not self.aircraft.ability.can("Hanging"):
                return False
            if self.aircraft.now_device <= 0:
                raise UnsupportedSubtaskException(f"航空器 {self.aircraft.name} 上没有吊运的设备")
        # 转移灾民
        elif self.type == "转移":
            if not self.aircraft.ability.can("Manned"):
                return False
            if "load_refugee" not in self.addition:
                raise MissingSubtaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_refugee 信息"
                )
            if (
                self.addition["load_refugee"] + self.aircraft.now_people
                > self.aircraft.max_capacity
            ):
                raise UnsupportedSubtaskException(
                    f'航空器 {self.aircraft.name} 无法转运灾民 {self.addition["load_refugee"]} 人'
                )
        elif self.type == "绞车转移":
            if not self.aircraft.ability.can("Manned", "Winch"):
                return False
            if "load_refugee" not in self.addition:
                raise MissingSubtaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_refugee 信息"
                )
            if (
                self.addition["load_refugee"] + self.aircraft.now_people
                > self.aircraft.max_capacity
            ):
                raise UnsupportedSubtaskException(
                    f'航空器 {self.aircraft.name} 无法转移灾民 {self.addition["load_refugee"]} 人'
                )
        elif self.type == "安置":
            if not self.aircraft.ability.can("Manned"):
                return False
            if self.aircraft.now_trapped_people <= 0:
                raise UnsupportedSubtaskException(f"航空器 {self.aircraft.name} 上没有要转移的灾民")
        # 转运伤患
        elif self.type == "转运":
            if not self.aircraft.ability.can("Manned", "Medical"):
                return False
            if "load_patient" not in self.addition:
                raise MissingSubtaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_patient 信息"
                )
            if (
                self.addition["load_patient"] + self.aircraft.now_people
                > self.aircraft.max_capacity
            ):
                raise UnsupportedSubtaskException(
                    f'航空器 {self.aircraft.name} 无法转运伤患 {self.addition["load_patient"]} 人'
                )
        elif self.type == "绞车转运":
            if not self.aircraft.ability.can("Manned", "Winch", "Medical"):
                return False
            if "load_patient" not in self.addition:
                raise MissingSubtaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_patient 信息"
                )
            if (
                self.addition["load_patient"] + self.aircraft.now_people
                > self.aircraft.max_capacity
            ):
                raise UnsupportedSubtaskException(
                    f'航空器 {self.aircraft.name} 无法转运灾民 {self.addition["load_patient"]} 人'
                )
        elif self.type == "交接":
            if not self.aircraft.ability.can("Manned", "Medical"):
                return False
            if self.aircraft.now_ill_people <= 0:
                raise UnsupportedSubtaskException(f"航空器 {self.aircraft.name} 上没有要交接的灾民")
        elif self.type == "加油保障":
            pass

        return True

    def check_position_valid(self) -> bool:
        """
        检查所指定的地点能否完成该任务
        """
        # check_aircraft_valid 确保了在相应前提下的 addition 某一 key 对应的 value 的存在

        # 通用需求
        # 此时未考虑多个飞机的情况，需要额外工作
        if self.type in SubTask._LAND_SUBTASK:
            if self.aircraft.type == "Helicopter":
                if self.aircraft.rotor_area > self.position.helicopter_area:
                    raise PositionNotSupportedException(
                        f"地点 {self.position.name} 的空间不支持航空器 {self.aircraft.name} 起降"
                    )
            elif self.aircraft.type == "FixedWing":
                if self.aircraft.rotor_area > self.position.fixed_area:
                    raise PositionNotSupportedException(
                        f"地点 {self.position.name} 的空间不支持航空器 {self.aircraft.name} 起降"
                    )
        elif self.type in SubTask._AIR_SUBTASK:
            if self.aircraft.air_area > self.position.air_work_area:
                raise PositionNotSupportedException(
                    f"地点 {self.position.name} 的空间不支持航空器 {self.aircraft.name} 空中作业"
                )
        # 侦查
        if self.type == "侦查搜寻":
            if (
                not isinstance(self.position, mpos.DisasterArea)
                or not self.position.search[0]
            ):
                raise PositionNotSupportedException(f"地点 {self.position.name} 不需要侦查搜寻")
        # 消防
        elif self.type == "取水":
            if not isinstance(self.position, mpos.NormalArea):
                raise PositionNotSupportedException(f"不能从地点 {self.position.name} 取水")
            if self.position.water < self.addition["load_water"]:
                raise PositionNotSupportedException(
                    f'地点 {self.position.name} 没有 {self.addition["load_water"]} 吨水'
                )
        elif self.type == "灭火":
            if not isinstance(self.position, mpos.DisasterArea):
                raise PositionNotSupportedException(f"地点 {self.position.name} 不需要水源灭火")
            if self.position.water >= self.position.need_water:
                raise SubTaskSucceedException(f"地点 {self.position.name} 的灭火任务已经完成")
        # 货运
        elif self.type == "装载":
            if not isinstance(self.position, mpos.NormalArea):
                raise PositionNotSupportedException(f"不能从地点 {self.position.name} 装载物资")
            if self.position.supply < self.addition["load_supply"]:
                raise PositionNotSupportedException(
                    f'地点 {self.position.name} 没有 {self.addition["load_supply"]} 千克物资'
                )
        elif self.type == "卸货":
            if not isinstance(self.position, mpos.DisasterArea):
                raise PositionNotSupportedException(f"地点 {self.position.name} 不需要卸载物资")
            if self.position.supply >= self.position.need_supply:
                raise SubTaskSucceedException(f"地点 {self.position.name} 的物资任务已经完成")
        # 载人
        elif self.type == "运送":
            if not isinstance(self.position, mpos.NormalArea):
                raise PositionNotSupportedException(f"不能从地点 {self.position.name} 运送人员")
            if self.position.rescue_people < self.addition["load_people"]:
                raise PositionNotSupportedException(
                    f'地点 {self.position.name} 没有 {self.addition["load_people"]} 个人员'
                )
        elif self.type == "投放" or self.type == "绞车投放":
            if not isinstance(self.position, mpos.DisasterArea):
                raise PositionNotSupportedException(
                    f"地点 {self.position.name} 不需要投放救援人员"
                )
            if self.position.rescue_people >= self.position.need_rescue_people:
                raise SubTaskSucceedException(f"地点 {self.position.name} 的投放人员任务已经完成")
        # 吊挂
        elif self.type == "吊运":
            if not isinstance(self.position, mpos.NormalArea):
                raise PositionNotSupportedException(f"不能从地点 {self.position.name} 吊运设备")
            if self.position.device < self.addition["load_device"]:
                raise PositionNotSupportedException(
                    f'地点 {self.position.name} 没有 {self.addition["load_device"]} 个设备'
                )
        elif self.type == "卸载":
            if not isinstance(self.position, mpos.DisasterArea):
                raise PositionNotSupportedException(f"地点 {self.position.name} 不需要卸载设备")
            if self.position.device >= self.position.need_device:
                raise SubTaskSucceedException(f"地点 {self.position.name} 的卸载设备任务已经完成")
        # 转移灾民
        elif self.type == "转移" or self.type == "绞车转移":
            if not isinstance(self.position, mpos.DisasterArea):
                raise PositionNotSupportedException(f"不能从地点 {self.position.name} 转移灾民")
            if self.position.trapped_people < self.addition["load_refugee"]:
                raise PositionNotSupportedException(
                    f'地点 {self.position.name} 没有 {self.addition["load_refugee"]} 个灾民'
                )
        elif self.type == "安置":
            if not isinstance(self.position, mpos.NormalArea):
                raise PositionNotSupportedException(f"地点 {self.position.name} 不能接受灾民")
        # 转运伤患
        elif self.type == "转运" or self.type == "绞车转运":
            if not isinstance(self.position, mpos.DisasterArea):
                raise PositionNotSupportedException(f"不能从地点 {self.position.name} 转运患者")
            if self.position.patient < self.addition["load_patient"]:
                raise PositionNotSupportedException(
                    f'地点 {self.position.name} 没有 {self.addition["load_patient"]} 个伤患'
                )
        elif self.type == "交接":
            if not isinstance(self.position, mpos.Hospital):
                raise PositionNotSupportedException(f"地点 {self.position.name} 不能接受伤患")
        elif self.type == "加油保障":
            if not isinstance(self.position, mpos.Airport):
                raise PositionNotSupportedException(
                    f"所选择的地点 {self.position.name} 不能进行加油保障"
                )

        # 特殊要求
        if self.position.special_condition is not None:
            if not self.position.special_condition(self.position, self.aircraft):
                raise SpecialConditionNotSatisfiedException(
                    f"地点 {self.position.name} 的特殊需求未满足"
                )

        return True

    def on_finish(self) -> None:
        if self.type == "加油保障":
            self.aircraft.current_fuel = self.aircraft.max_fuel
        elif self.type == "装载":
            self.aircraft.now_supply = self.addition["load_supply"]
            self.position.supply -= self.addition["load_supply"]
        elif self.type == "卸货":
            self.position.supply += self.aircraft.now_supply
            self.aircraft.now_supply = 0
        elif self.type == "运送":
            self.aircraft.now_resuce_people += self.addition["load_people"]
            self.position.rescue_people -= self.addition["load_people"]
        elif self.type == "投放" or self.type == "绞车投放":
            self.position.rescue_people += self.aircraft.now_resuce_people
            self.aircraft.now_resuce_people = 0
        elif self.type == "吊运":
            self.aircraft.now_device = self.addition["load_device"]
            self.position.device -= self.addition["load_device"]
        elif self.type == "卸载":
            self.position.device += self.aircraft.now_device
            self.aircraft.now_device = 0
        elif self.type == "转移" or self.type == "绞车转移":
            self.aircraft.now_trapped_people += self.addition["load_refugee"]
            self.position.trapped_people -= self.addition["load_refugee"]
        elif self.type == "安置":
            self.position.trapped_people += self.aircraft.now_trapped_people
            self.aircraft.now_trapped_people = 0
        elif self.type == "转运" or self.type == "绞车转运":
            self.aircraft.now_ill_people += self.addition["load_patient"]
            self.position.patient -= self.addition["load_patient"]
        elif self.type == "交接":
            self.position.patient += self.aircraft.now_ill_people
            self.aircraft.now_ill_people = 0
        elif self.type == "取水":
            self.aircraft.now_water += self.addition["load_water"]
            self.position.water -= self.addition["load_water"]
        elif self.type == "灭火":
            self.position.water += self.aircraft.now_water
            self.aircraft.now_water = 0
        elif self.type == "侦查搜寻":
            tmp: mpos.DisasterArea = self.position  # type: ignore
            tmp.already_search = tmp.search[1]
        else:
            raise UnsupportedSubtaskException(f"不支持的子任务类型 {self.type}")


def _attach_fset_侦查(self: mpos.DisasterArea, value: float, task: "Task") -> None:
    self._attach_already_search = value  # type: ignore

    if self._attach_already_search >= self.search[1]:  # type: ignore
        task.is_finished = True


def _attach_fset_灭火(self: mpos.DisasterArea, value: int, task: "Task") -> None:
    self._attach_water = value  # type: ignore

    if self._attach_water >= self.need_water:  # type: ignore
        task.is_finished = True


def _attach_fset_卸货(self: mpos.DisasterArea, value: int, task: "Task") -> None:
    self._attach_supply = value  # type: ignore

    if self._attach_supply >= self.need_supply:  # type: ignore
        task.is_finished = True


def _attach_fset_吊挂(self: mpos.DisasterArea, value: int, task: "Task") -> None:
    self._attach_rescue_people = value  # type: ignore

    if self._attach_rescue_people >= self.need_rescue_people:  # type: ignore
        task.is_finished = True


def _attach_fset_载人(self: mpos.DisasterArea, value: int, task: "Task") -> None:
    self._attach_device = value  # type: ignore

    if self._attach_device >= self.need_device:  # type: ignore
        task.is_finished = True


def _attach_fset_灾民(self: mpos.DisasterArea, value: int, task: "Task") -> None:
    self._attach_trapped_people = value  # type: ignore

    if self._attach_trapped_people <= 0:  # type: ignore
        task.is_finished = True


def _attach_fset_伤患(self: mpos.DisasterArea, value: int, task: "Task") -> None:
    self._attach_patient = value  # type: ignore

    if self._attach_patient <= 0:  # type: ignore
        task.is_finished = True


class Task:
    def __init__(
        self,
        scene: Scene,
        t_type: TaskType,
        position: mpos.DisasterArea,
        /,
        on_finished: Optional[Callable[[Scene, "Task"], None]] = None,
    ) -> None:
        self.scene: Scene = scene
        self.position: mpos.DisasterArea = position
        self.type: TaskType = t_type
        self.is_finished: bool = False

        if self.position not in self.scene.map.position:
            raise PositionNotExistException(f"地点 {self.position.name} 不存在")

        self.on_finished: Callable[[Scene, "Task"], None] = (
            on_finished if on_finished is not None else lambda scene, task: None
        )

        self.attach()

    def attach(self) -> None:
        mtask = self
        # 侦查
        if self.type == "侦查搜寻":
            setattr(
                self.position, "_attach_already_search", self.position.already_search
            )
            del self.position.already_search
            setattr(
                self.position,
                "already_search",
                property(
                    lambda self: self._attach_already_search,
                    lambda self, value: _attach_fset_侦查(self, value, mtask),
                ),
            )
        # 消防
        elif self.type == "灭火":
            setattr(self.position, "_attach_water", self.position.water)
            del self.position.need_water
            setattr(
                self.position,
                "water",
                property(
                    lambda self: self._attach_water,
                    lambda self, value: _attach_fset_灭火(self, value, mtask),
                ),
            )
        # 货运
        elif self.type == "卸货":
            setattr(self.position, "_attach_supply", self.position.supply)
            del self.position.supply
            setattr(
                self.position,
                "supply",
                property(
                    lambda self: self._attach_supply,
                    lambda self, value: _attach_fset_卸货(self, value, mtask),
                ),
            )
        # 载人
        elif self.type == "投放" or self.type == "绞车投放":
            setattr(self.position, "_attach_rescue_people", self.position.rescue_people)
            del self.position.rescue_people
            setattr(
                self.position,
                "rescue_people",
                property(
                    lambda self: self._attach_rescue_people,
                    lambda self, value: _attach_fset_载人(self, value, mtask),
                ),
            )
        # 吊挂
        elif self.type == "卸载":
            setattr(self.position, "_attach_device", self.position.device)
            del self.position.device
            setattr(
                self.position,
                "device",
                property(
                    lambda self: self._attach_device,
                    lambda self, value: _attach_fset_吊挂(self, value, mtask),
                ),
            )
        # 转移灾民
        elif self.type == "转移" or self.type == "绞车转移":
            setattr(
                self.position, "_attach_trapped_people", self.position.trapped_people
            )
            del self.position.trapped_people
            setattr(
                self.position,
                "trapped_people",
                property(
                    lambda self: self._attach_trapped_people,
                    lambda self, value: _attach_fset_灾民(self, value, mtask),
                ),
            )
        # 转运伤患
        elif self.type == "转运" or self.type == "绞车转运":
            setattr(self.position, "_attach_patient", self.position.patient)
            del self.position.patient
            setattr(
                self.position,
                "patient",
                property(
                    lambda self: self._attach_patient,
                    lambda self, value: _attach_fset_伤患(self, value, mtask),
                ),
            )
        elif self.type in ["取水", "加油保障", "装载", "运送", "吊运", "安置", "交接"]:
            raise NotSupportedTaskException(f"类型 {self.type} 不能作为任务")
