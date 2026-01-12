from datetime import date, time
from datetime import datetime as cdatetime  # 有时候会返回datatime类型
from sqlalchemy.orm import class_mapper
from sqlalchemy.engine.row import Row
from app import db
# from flask_sqlalchemy.model import Model
from sqlalchemy import DateTime, Numeric, Date, Time  # 有时又是DateTime


def get_plain_password(password):
    if password == '':
        return ''
    else:
        return password


# 序列化查询结果
from collections.abc import Iterable


def query_to_dict(data):
    """
    将SQLAlchemy查询结果转换为字典或字典列表
    :param data: SQLAlchemy查询结果（单个对象、命名元组、列表/查询集）
    :return: 字典或字典列表
    """
    # 空值处理
    if not data:
        return []

    # 定义单条数据转换的内部函数
    def convert_single(item):
        if hasattr(item, '_fields'):
            return {field: getattr(item, field) for field in item._fields}
        try:
            return model_to_dict(item)
        except (NameError, AttributeError):
            item_dict = item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)
            return item_dict

    # 判断是否为多条数据（可迭代且非单个对象）
    is_multiple = False
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        # 尝试判断是否为多条数据（SQLAlchemy Query/列表/元组）
        try:
            # 若为单个对象（如Row/模型实例），迭代会报错，捕获并处理
            iter(data)
            is_multiple = True
        except TypeError:
            is_multiple = False

    if not is_multiple:
        return convert_single(data)

    # 处理多条数据
    return [convert_single(item) for item in data]


# 当结果为result对象列表时，result有key()方法
def result_to_dict(results):
    res = [dict(zip(r.keys(), r)) for r in results]
    # 这里r为一个字典，对象传递直接改变字典属性
    for r in res:
        find_datetime(r)
        return res


def model_to_dict(model):
    """
    将单个模型对象转换为字典
    """
    # 处理Row对象（使用with_entities查询的结果）
    if isinstance(model, Row):
        return {col.key: getattr(model, col.key) for col in model._fields}

    # 处理ORM对象
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return {col: getattr(model, col) for col in columns}


def find_datetime(value):
    for v in value:
        if (isinstance(value[v], cdatetime)):
            value[v] = convert_datetime(value[v])  # 这里原理类似，修改的字典对象，不用返回即可修改


def convert_datetime(value):
    if value:
        if isinstance(value, (cdatetime, DateTime)):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (date, Date)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, (Time, time)):
            return value.strftime("%H:%M:%S")
        else:
            return ""
