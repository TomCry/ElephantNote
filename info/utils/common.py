# 共用的工具类

def to_index_class(index):

    """返回指定索引对应的类名"""
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"

    return ""