from typing import Literal, Any, TypedDict, Unpack, NotRequired
from .scene import Scene
from .aircraft import Aircraft
from .map import Position

SubTaskType = (
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


class UnsupportedTaskException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MissingTaskInformationException(Exception):
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
    # 绞车转移灾民数量
    load_winch_refugee: NotRequired[int]
    # 安置灾民数量
    # unload_refugee: NotRequired[int]
    # 转运伤患数量
    load_patient: NotRequired[int]
    # 绞车转运伤患数量
    load_winch_patient: NotRequired[int]
    # 交接伤患数量
    # unload_patient: NotRequired[int]
    # 取水数量
    load_water: NotRequired[int]
    # 灭火用水数量
    # unload_water: NotRequired[int]


class SubTask:
    def __init__(
        self,
        scene: Scene,
        task_type: SubTaskType,
        aircraft: Aircraft,
        position: Position,
        **kwargs: Unpack[SubTaskParams],
    ) -> None:
        # 所属推演场景
        self.scene: Scene = scene
        # 所属子任务类型
        self.type: SubTaskType = task_type
        # 执行任务的航空器
        self.aircraft: Aircraft = aircraft
        # 执行任务的地点
        self.position: Position = position
        # 任务附加信息
        self.addition: SubTaskParams = kwargs

        if not self.check_valid():
            raise UnsupportedTaskException(
                f"航空器 {self.aircraft.name} 不能执行 {self.type} 任务"
            )

    #  检验所指派的航空器能否执行该任务
    def check_valid(self) -> bool:
        # 侦查
        if self.type == "侦查搜寻":
            if not self.aircraft.ability.can("Reconnoitre"):
                return False
        # 消防
        elif self.type == "取水":
            if not self.aircraft.ability.can("Fire"):
                return False
            if "load_water" not in self.addition:
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_water 信息"
                )
            if self.addition["load_water"] > self.aircraft.max_external_load:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法取水 {self.addition["load_water"]} 吨'
                )
        elif self.type == "灭火":
            if not self.aircraft.ability.can("Fire"):
                return False
            if self.aircraft.now_water <= 0:
                raise UnsupportedTaskException(f"航空器 {self.aircraft.name} 上没有多余的水")

        return True


class Task:
    ...
