def read_trajectory_data(file_path, delimiter=None, column_names=None):
    """
    读取轨迹数据文件并解析为字典列表
    :param file_path: 文件路径
    :param delimiter: 分隔符（默认为 None，表示使用任意空白字符分割）
    :param column_names: 列名列表，例如 ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz']
    :return: 包含轨迹数据的字典列表
    """
    if column_names is None:
        raise ValueError("必须提供 column_names 参数！")

    data = []
    with open(file_path, 'r') as file:
        for line in file:
            # 去除空白字符并分割
            if delimiter:
                values = line.strip().split(delimiter)
            else:
                # 如果未指定分隔符，则使用 split() 默认行为（任意空白字符分割）
                values = line.strip().split()

            # 将每行数据转换为字典
            row = {column_names[i]: float(values[i]) for i in range(len(column_names))}
            data.append(row)
    return data
