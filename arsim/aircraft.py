from typing import Literal

AircraftAbilitySpecial = ( Literal["Reconnoitre"] | Literal["Freight"] | Literal["Hanging"] | Literal["Manned"] | Literal["Winch"] 
                             | Literal["Medical"] | Literal["Fire"] | Literal["Sea"] )
AircraftType = Literal["Helicopter"] | Literal["FixedWing"]

class AircraftAbility:
    _map = { "Reconnoitre": 0b1, "Freight": 0b10, "Hanging": 0b100, "Manned": 0b1000,
             "Winch": 0b1_0000, "Medical": 0b10_0000, "Fire": 0b100_0000, "Sea": 0b1000_0000 }
    # 侦察功能
    Reconnoitre = 0b1
    # 货运功能
    Freight = 0b10
    # 吊挂功能
    Hanging = 0b100
    # 载人功能
    Manned = 0b1000
    # 绞车功能
    Winch = 0b1_0000
    # 医护功能
    Medical = 0b10_0000
    # 消防功能
    Fire = 0b100_0000
    # 海上功能
    Sea = 0b1000_0000

    def __init__(self, *args: AircraftAbilitySpecial) -> None:
        self.map = 0
        for _key in AircraftAbility._map:
            if _key in args:
                self.map |= AircraftAbility._map[_key]
        
    def can(self, ability: AircraftAbilitySpecial) -> bool:
        return AircraftAbility._map[ability] & self.map != 0


class Aircraft:
    def __init__( self, price: float, name: str, ability: AircraftAbility, rotor_area: float, air_area: float,
                  max_fuel: float, cruising_speed: float, fuel_consumption_per_unit_time: float, max_capacity: int, 
                  max_internal_load: float, max_external_load: float, * , fuel_fill_time: float = 1200, 
                  person_on_off_time: float = 60, supply_load_time: float = 0.1, device_load_time: float = 1200, 
                  patient_on_off_time: float = 600, water_weight: float = 3, water_load_time: float = 900, 
                  extinguishing_time: float = 900, search_time: float = 10.68, winch_person_time: float = 150, 
                  winch_patient_time: float = 600, type: AircraftType = "Helicopter", current_fuel: float = 0) -> None:
        # 飞机属性
        self.name: str = name
        # 飞机价格（亿元）
        self.price: float = price
        # 当前油量，油量为 0 时，飞机自动迫降
        self.current_fuel: float = current_fuel
        # 功能
        self.ability: AircraftAbility = ability
        # 旋翼面积（m2）
        self.rotor_area: float = rotor_area
        # 空中作业限制（m2）
        self.air_area: float = air_area
        # 最大油量
        self.max_fuel: float = max_fuel
        # 巡航速度
        self.cruising_speed: float = cruising_speed
        # 单位时间耗油量
        self.fuel_consumption_per_unit_time: float = fuel_consumption_per_unit_time
        # 最大载人数量
        self.max_capacity: int = max_capacity
        # 内载荷上限（kg）
        self.max_internal_load: float = max_internal_load
        # 外载荷上限（kg）
        self.max_external_load: float = max_external_load
        # 单次保障加油时间（秒）
        self.fuel_fill_time: float = fuel_fill_time
        # 单个人员上下级时间（秒）
        self.person_on_off_time: float = person_on_off_time
        # 单位物资装卸时间（秒）
        self.supply_load_time: float = supply_load_time
        # 大型设备装卸时间（秒）
        self.device_load_time: float = device_load_time
        # 单个患者上下机时间（秒）
        self.patient_on_off_time: float = patient_on_off_time
        # 单次消防取水重量（吨）
        self.water_weight: float = water_weight
        # 单次取水作业时间（秒）
        self.water_load_time: float = water_load_time
        # 单次灭火时间（秒）
        self.extinguishing_time: float = extinguishing_time
        # 单位面积搜查/搜寻时间（秒）
        self.search_time: float = search_time
        # 单个人员绞车上下机时间（秒）
        self.winch_person_time: float = winch_person_time
        # 单个伤患绞车上下机时间（秒）
        self.winch_patient_time: float = winch_patient_time
        
        # 携带的救援物资量
        self.now_supply: int = 0
        # 携带的救援人员数量
        self.now_resuce_people: int = 0
        # 吊运的救援设备数量
        self.now_device: int = 0
        # 携带的受困群众数量
        self.now_trapped_people: int = 0
        # 携带的重病患者数量
        self.now_ill_people: int = 0
        # 携带的水量
        self.now_water: int = 0
