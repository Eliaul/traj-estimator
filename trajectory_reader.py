import numpy as np
from scipy.spatial.transform import Rotation

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

    # 检查是否包含四元数列
    has_quaternion = all(col in column_names for col in ['qx', 'qy', 'qz', 'qw'])

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

            if has_quaternion:
                qx = row['qx']
                qy = row['qy']
                qz = row['qz']
                qw = row['qw']

                # 将四元数转换为欧拉角（单位：弧度）
                rotation = Rotation.from_quat([qx, qy, qz, qw])
                euler_angles = rotation.as_euler('xyz', degrees=True)  # 返回 roll, pitch, yaw

                # 将欧拉角存入字典
                row['roll'] = euler_angles[0]
                row['pitch'] = euler_angles[1]
                row['yaw'] = euler_angles[2]

            data.append(row)
    return data
