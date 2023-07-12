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

        if not self.check_aircraft_valid():
            raise UnsupportedTaskException(
                f"航空器 {self.aircraft.name} 不能执行 {self.type} 任务"
            )

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
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_water 信息"
                )
            if (
                self.addition["load_water"] + self.aircraft.now_external
                > self.aircraft.max_external_load
            ):
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法取水 {self.addition["load_water"]} 吨'
                )
        elif self.type == "灭火":
            if not self.aircraft.ability.can("Fire"):
                return False
            if self.aircraft.now_water <= 0:
                raise UnsupportedTaskException(f"航空器 {self.aircraft.name} 上没有多余的水")
        # 货运
        elif self.type == "装载":
            if not self.aircraft.ability.can("Freight"):
                return False
            if "load_supply" not in self.addition:
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_supply 信息"
                )
            if (
                self.addition["load_supply"] + self.aircraft.now_internal
                > self.aircraft.max_internal_load
            ):
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法装载救援物资 {self.addition["load_supply"]} 千克'
                )
        elif self.type == "卸货":
            if not self.aircraft.ability.can("Freight"):
                return False
            if self.aircraft.now_supply <= 0:
                raise UnsupportedTaskException(f"航空器 {self.aircraft.name} 上没有装载的物资")
        # 载人
        elif self.type == '运送':
            if not self.aircraft.ability.can("Manned"):
                return False
            if "load_people" not in self.addition:
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_people 信息"
                )
            if (
                self.aircraft.now_people + self.addition["load_people"]
                > self.aircraft.max_capacity
            ):
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法运送人员 {self.addition["load_people"]} 人'
                )
        elif self.type == "投放":
            if not self.aircraft.ability.can("Manned"):
                return False
            if self.aircraft.now_resuce_people <= 0:
                raise UnsupportedTaskException(f"航空器 {self.aircraft.name} 上没有救援人员")
        elif self.type == "绞车投放":
            if not self.aircraft.ability.can("Manned", "Winch"):
                return False
            if self.aircraft.now_resuce_people <= 0:
                raise UnsupportedTaskException(f"航空器 {self.aircraft.name} 上没有救援人员")
        # 吊挂
        elif self.type == '吊运':
            if not self.aircraft.ability.can('Hanging'):
                return False
            if self.aircraft.now_external + 10_000 > self.aircraft.max_external_load:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法吊运 10 吨的设备'
                )
        elif self.type == '卸载':
            if not self.aircraft.ability.can('Hanging'):
                return False
            if self.aircraft.now_device <= 0:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 上没有吊运的设备'
                )
        # 转移灾民
        elif self.type == '转移':
            if not self.aircraft.ability.can('Manned'):
                return False
            if 'load_refugee' not in self.addition:
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_refugee 信息"
                )
            if self.addition['load_refugee'] + self.aircraft.now_people > self.aircraft.max_capacity:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法转运灾民 {self.addition["load_refugee"]} 人'
                )
        elif self.type == '绞车转移':
            if not self.aircraft.ability.can('Manned', 'Winch'):
                return False
            if 'load_refugee' not in self.addition:
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_refugee 信息"
                )
            if self.addition['load_refugee'] + self.aircraft.now_people > self.aircraft.max_capacity:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法转移灾民 {self.addition["load_refugee"]} 人'
                )
        elif self.type == '安置':
            if not self.aircraft.ability.can('Manned'):
                return False
            if self.aircraft.now_trapped_people <= 0:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 上没有要转移的灾民'
                )
        # 转运伤患
        elif self.type == '转运':
            if not self.aircraft.ability.can('Manned', 'Medical'):
                return False
            if 'load_patient' not in self.addition:
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_patient 信息"
                )
            if self.addition['load_patient'] + self.aircraft.now_people > self.aircraft.max_capacity:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法转运伤患 {self.addition["load_patient"]} 人'
                )
        elif self.type == '绞车转运':
            if not self.aircraft.ability.can('Manned', 'Winch', 'Medical'):
                return False
            if 'load_patient' not in self.addition:
                raise MissingTaskInformationException(
                    f"航空器 {self.aircraft.name} 执行 {self.type} 任务时缺少 load_patient 信息"
                )
            if self.addition['load_patient'] + self.aircraft.now_people > self.aircraft.max_capacity:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 无法转运灾民 {self.addition["load_patient"]} 人'
                )
        elif self.type == '交接':
            if not self.aircraft.ability.can('Manned', 'Medical'):
                return False
            if self.aircraft.now_ill_people <= 0:
                raise UnsupportedTaskException(
                    f'航空器 {self.aircraft.name} 上没有要交接的灾民'
                )
        elif self.type == '加油保障':
            pass

        return True

    def check_position_valid(self) -> bool:
        """
        检查所指定的地点能否完成该任务
        """

        return True


class Task:
    ...
