# SoSAirRescue

## 使用方法

```sh
python ./SoSAirRescue.py simulate
```

## 导入文件格式

```python
class SoSData:
    def create_map(self):
        """创建地图，返回 Map
        """
        ...

    def create_aircraft(self):
        """创建飞机，返回 list[Aircraft]
        """
        ...

    def on_init(self):
        """初始化，在此添加 Task 和 Subtask
        """
        ...

    def on_subtask_finish(self):
        """当每一个 subtask 完成时调用
        """
        ...
```