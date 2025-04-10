import numpy as np
from scipy.spatial.transform import Rotation as R


def load_data(file_path, delimiter=None):
    """
    从文件加载数据
    :param file_path: 文件路径
    :param delimiter: 分隔符，默认为空格
    :return: 数据列表（每行是一个列表）
    """
    with open(file_path, 'r') as file:
        if delimiter:
            data = [line.strip().split(delimiter) for line in file if line.strip()]
        else:
            data = [line.strip().split() for line in file if line.strip()]

    return data


def parse_pose(data, time_col, pos_cols, orient_cols, orient_format='quat'):
    """
    解析位姿数据，提取时间、位置和姿态
    :param data: 原始数据列表
    :param time_col: 时间列的索引
    :param pos_cols: 位置列的索引列表 [x, y, z]
    :param orient_cols: 姿态列的索引列表 [qx, qy, qz, qw] 或 [roll, pitch, yaw]
    :param orient_format: 姿态格式，'quat' 或 'euler'
    :return: 时间 (float), 平移向量 (np.array), 姿态 (np.array)
    """
    time = float(data[time_col])
    position = np.array([float(data[i]) for i in pos_cols])

    if orient_format == 'quat':
        orientation = np.array([float(data[i]) for i in orient_cols])
    elif orient_format == 'euler':
        orientation = np.array([float(data[i]) for i in orient_cols])
    else:
        raise ValueError("Invalid orientation format. Use 'quat' or 'euler'.")

    return time, position, orientation


def compute_relative_position(current_position, origin, origin_quat):
    """
    计算当前点相对于原点的位置，考虑原点姿态的影响
    :param current_position: 当前点的位置 (np.array)
    :param origin: 新坐标系的原点 (np.array)
    :param origin_quat: 原点姿态的四元数 (np.array)
    :return: 相对位置 (np.array)
    """
    # 将原点姿态转换为旋转矩阵
    r_origin = R.from_quat(origin_quat)

    # 计算当前点相对于原点的偏移（全局坐标系）
    global_offset = current_position - origin

    # 将偏移向量转换到原点姿态的局部坐标系
    relative_position = r_origin.inv().apply(global_offset)

    return relative_position


def compute_relative_time(current_time, origin_time):
    """
    计算当前点相对于原点的时间
    :param current_time: 当前点的时间
    :param origin_time: 原点的时间
    :return: 相对时间
    """
    return current_time


def compute_relative_orientation(current_quat, origin_quat, orient_format='quat'):
    """
    计算当前姿态相对于原点姿态的旋转
    :param current_quat: 当前姿态的四元数 (np.array)
    :param origin_quat: 原点姿态的四元数 (np.array)
    :param orient_format: 姿态格式，'quat' 或 'euler'
    :return: 相对姿态 (np.array)
    """
    r_origin = R.from_quat(origin_quat)
    r_current = R.from_quat(current_quat)
    relative_rotation = r_current * r_origin.inv()

    if orient_format == 'quat':
        return relative_rotation.as_quat()
    elif orient_format == 'euler':
        return relative_rotation.as_euler('xyz', degrees=True)
    else:
        raise ValueError("Invalid orientation format. Use 'quat' or 'euler'.")


def transform_data(data, time_col, pos_cols, orient_cols, orient_format='quat'):
    """
    将数据转换为以第一行为坐标系的相对位置和姿态
    :param data: 原始数据列表
    :param time_col: 时间列的索引
    :param pos_cols: 位置列的索引列表 [x, y, z]
    :param orient_cols: 姿态列的索引列表 [qx, qy, qz, qw] 或 [roll, pitch, yaw]
    :param orient_format: 姿态格式，'quat' 或 'euler'
    :return: 转换后的数据列表，每行是 [时间, x坐标, y坐标, z坐标, 姿态分量...]
    """
    # 提取第一行的数据作为新坐标系的原点和姿态
    first_row = data[0]
    origin_time, origin_position, origin_orientation = parse_pose(first_row, time_col, pos_cols, orient_cols,
                                                                  orient_format)

    # 如果姿态是欧拉角，转换为四元数以便计算
    if orient_format == 'euler':
        origin_quat = R.from_euler('xyz', origin_orientation, degrees=True).as_quat()
    else:
        origin_quat = origin_orientation

    transformed_data = []
    for row in data:
        # 解析当前行的位姿数据
        time, position, orientation = parse_pose(row, time_col, pos_cols, orient_cols, orient_format)

        # 如果姿态是欧拉角，转换为四元数以便计算
        if orient_format == 'euler':
            current_quat = R.from_euler('xyz', orientation, degrees=True).as_quat()
        else:
            current_quat = orientation

        # 计算相对时间、位置和姿态
        relative_time = compute_relative_time(time, origin_time)
        relative_position = compute_relative_position(position, origin_position, origin_quat)
        relative_orientation = compute_relative_orientation(current_quat, origin_quat, orient_format)

        # 将结果添加到转换后的数据列表中
        transformed_data.append([relative_time] + relative_position.tolist() + relative_orientation.tolist())

    return transformed_data


def save_data(file_path, data, column_order, delimiter=None, decimal_places=6):
    """
    保存转换后的数据到文件，并指定保留小数位数
    :param file_path: 文件路径
    :param data: 转换后的数据列表
    :param column_order: 列的顺序，例如 ['time', 'x', 'y', 'z', 'roll', 'pitch', 'yaw']
    :param delimiter: 分隔符，默认为 None
    :param decimal_places: 保留的小数位数，默认为 6
    """
    if not delimiter:
        delimiter = ' '

    with open(file_path, 'w') as file:
        for row in data:
            # 根据列顺序重新排列数据
            formatted_row = []
            for col in column_order:
                if col == 'time':
                    formatted_row.append(f"{row[0]:.{decimal_places}f}")
                elif col in ['x', 'y', 'z']:
                    idx = ['x', 'y', 'z'].index(col) + 1
                    formatted_row.append(f"{row[idx]:.{decimal_places}f}")
                elif col in ['roll', 'pitch', 'yaw']:
                    idx = 4 + ['roll', 'pitch', 'yaw'].index(col)
                    formatted_row.append(f"{row[idx]:.{decimal_places}f}")
                elif col in ['qx', 'qy', 'qz', 'qw']:
                    idx = 4 + ['qx', 'qy', 'qz', 'qw'].index(col)
                    formatted_row.append(f"{row[idx]:.{decimal_places}f}")
            line = delimiter.join(formatted_row)
            file.write(line + '\n')


def main(input_file, output_file, time_col, pos_cols, orient_cols, orient_format='quat', delimiter=None,
         decimal_places=6):
    """
    主函数：加载数据、转换数据并保存结果
    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    :param time_col: 时间列的索引
    :param pos_cols: 位置列的索引列表 [x, y, z]
    :param orient_cols: 姿态列的索引列表 [qx, qy, qz, qw] 或 [roll, pitch, yaw]
    :param orient_format: 姿态格式，'quat' 或 'euler'
    :param delimiter: 分隔符，默认为空格
    :param decimal_places: 保留的小数位数，默认为 6
    """
    # 加载数据
    data = load_data(input_file, delimiter)

    # 确定列顺序
    column_order = []
    for i, val in enumerate(data[0]):
        if i == time_col:
            column_order.append('time')
        elif i in pos_cols:
            column_order.append(['x', 'y', 'z'][pos_cols.index(i)])
        elif i in orient_cols:
            if orient_format == 'quat':
                column_order.append(['qx', 'qy', 'qz', 'qw'][orient_cols.index(i)])
            else:
                column_order.append(['roll', 'pitch', 'yaw'][orient_cols.index(i)])

    # 转换数据
    transformed_data = transform_data(data, time_col, pos_cols, orient_cols, orient_format)

    # 保存结果
    save_data(output_file, transformed_data, column_order, delimiter, decimal_places)
    print(f"转换完成！结果已保存到 {output_file}")


if __name__ == "__main__":
    # 示例调用
    input_file = "./data/20231105/data2/tls_T_imu.txt"  # 输入文件路径
    output_file = "./data/20231105/data2/ref.txt"  # 输出文件路径
    time_col = 0  # 时间列的索引
    pos_cols = [1, 2, 3]  # 位置列的索引 [x, y, z]
    orient_cols = [4, 5, 6, 7]  # 姿态列的索引 [qx, qy, qz, qw]
    orient_format = 'quat'  # 姿态格式，'quat' 或 'euler'
    delimiter = None  # 分隔符
    decimal_places = 6  # 保留的小数位数

    main(input_file, output_file, time_col, pos_cols, orient_cols, orient_format, delimiter, decimal_places)
