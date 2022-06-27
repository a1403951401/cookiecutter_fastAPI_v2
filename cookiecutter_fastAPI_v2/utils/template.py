import datetime
import re
from typing import Any


class Template:
    format_map: dict = {}
    format_data: str
    data: dict

    def __init__(self, format_data: str, data: dict):
        self.format_data = format_data
        self.data = data

    def format_key(self, key: str, data: Any) -> Any:
        data = data or self.data
        # 字典取value
        if isinstance(data, dict):
            return data.get(key)
        # list 取下标
        if isinstance(data, (list, tuple)):
            return data[int(key)] if len(data) > int(key) else None
        if isinstance(data, datetime.datetime):
            return datetime.datetime.strftime(data, '%Y-%m-%d %H:%M:%S')
        # 字符串 / 数字等其他对象不存在 key 返回 None 字符串！
        if key:
            return None
        return data

    def get_data(self, key: str, data) -> Any:
        key = key.split('.', 1)
        if len(key) > 1:
            return self.get_data(key[1], self.format_key(key[0], data))
        return self.format_key(key[0], data)

    def get_format_map(self) -> dict:
        # 格式化 format 对象
        for item in set([i for i in re.compile(r'{{.*?}}').findall(self.format_data)]):
            format_key = item[2:-2].strip()
            # 去除两边括号以及空格
            for key, info in self.data.items():
                if format_key[:len(key)] == key:
                    self.format_map[item] = str(self.get_data(format_key[len(key) + 1:], info))
                    break
            else:
                self.format_map[item] = str(None)
        return self.format_map

    def __str__(self) -> str:
        format_map: dict = self.get_format_map()
        format_data = self.format_data
        for k, v in format_map.items():
            format_data = format_data.replace(k, v)
        return format_data


if __name__ == '__main__':
    t = Template(
        """
        {{ str }}
        {{ dict.key }}
        {{ dict.key.key2 }}
        {{ list.0 }}
        {{ list.2 }}
        {{ time }}
        """,
        {
            'str': '字符串',
            'dict': {
                'key': {
                    'key2': 'key2'
                }
            },
            'list': ['123', 222, '333'],
            'time': datetime.datetime.now()
        }
    )
    # print(str(t))

    t = Template("""{{iconf}}花小猪又为你节省{{reduce_fee}}元！您的小猪特快订单因实际行驶未达到一口价预估里程，已为你重新计算车费~""",
        {
            'iconf': '🚀',
            'reduce_fee': 10
        }
    )
    print(str(t))
