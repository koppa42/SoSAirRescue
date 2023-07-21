from importlib import util
from os import path
import sys


class Module:
    def __init__(self, file_path: str):
        """从文件导入模块

        Args:
            file_path (str): 模块的路径

        Raises:
            FileNotFoundError: 找不到模块

        Returns:
            _type_: _description_
        """
        # 获取模块名称
        absolute_path = path.abspath(file_path)
        if not path.exists(absolute_path):
            raise FileNotFoundError(f"文件 {absolute_path} 不存在")
        module_name = path.splitext(path.basename(absolute_path))[0]

        # 加载模块
        module_dir = path.dirname(absolute_path)
        sys.path.append(module_dir)

        spec = util.spec_from_file_location(module_name, absolute_path)
        if spec is None:
            raise FileNotFoundError(f"文件 {absolute_path} 不存在")

        module = util.module_from_spec(spec)
        if spec.loader is None:
            raise FileNotFoundError(f"文件 {absolute_path} 不存在")

        spec.loader.exec_module(module)
        self.module = module

        from ..api import SoSAPI

        # 对以 SoS 开头的类均进行注入
        for cls in self.module.__dict__.values():
            if type(cls) == type and cls.__name__.startswith("SoS") :
                cls.api = SoSAPI()  # type: ignore [reportGeneralTypeIssues, attr-defined]

    @staticmethod
    def from_file(file_path: str) -> "Module":
        """从文件导入模块

        Args:
            file_path (str): 模块的路径

        Returns:
            Module: 封装的模块
        """
        return Module(file_path)

    def get(self, name: str):
        return self.module.__dict__[name] if name in self.module.__dict__ else None

    def __getitem__(self, name: str):
        return self.get(name)
