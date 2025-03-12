import numpy as np
from scipy.spatial.transform import Rotation as R


def load_data(file_path, delimiter=' '):
    """
    从文件加载数据
    :param file_path: 文件路径
    :param delimiter: 分隔符，默认为空格
    :return: 数据列表（每行是一个列表）
    """
    with open(file_path, 'r') as file:
        data = [line.strip().split(delimiter) for line in file if line.strip()]
    return data


def parse_data(data, time_col, pos_cols, orient_cols, orient_format='quat'):
    """
    解析数据，提取时间、位置和姿态
    :param data: 原始数据列表
    :param time_col: 时间列的索引
    :param pos_cols: 位置列的索引列表 [x, y, z]
    :param orient_cols: 姿态列的索引列表 [qx, qy, qz, qw] 或 [roll, pitch, yaw]
    :param orient_format: 姿态格式，'quat' 或 'euler'
    :return: 解析后的数据列表，每行是 [时间, 位置, 姿态]
    """
    parsed_data = []
    for row in data:
        time = float(row[time_col])
        position = np.array([float(row[i]) for i in pos_cols])

        if orient_format == 'quat':
            orientation = np.array([float(row[i]) for i in orient_cols])
        elif orient_format == 'euler':
            # 将欧拉角转换为四元数
            roll, pitch, yaw = [float(row[i]) for i in orient_cols]
            orientation = R.from_euler('xyz', [roll, pitch, yaw], degrees=False).as_quat()
        else:
            raise ValueError("Invalid orientation format. Use 'quat' or 'euler'.")

        parsed_data.append([time, position, orientation])
    return parsed_data


def extract_first_row(parsed_data):
    """
    提取第一行的数据作为新坐标系的原点和姿态
    :param parsed_data: 解析后的数据列表
    :return: 原点 (np.array), 姿态四元数 (np.array)
    """
    first_row = parsed_data[0]
    origin = first_row[1]  # 位置
    q_origin = first_row[2]  # 姿态
    return origin, q_origin


def compute_relative_position(current_position, origin, current_quat, origin_quat):
    """
    计算当前点相对于原点的位置，考虑原点姿态和当前姿态的影响
    :param current_position: 当前点的位置 (np.array)
    :param origin: 新坐标系的原点 (np.array)
    :param current_quat: 当前姿态的四元数 (np.array)
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


def compute_relative_orientation(current_quat, origin_quat):
    """
    计算当前姿态相对于原点姿态的旋转
    :param current_quat: 当前姿态的四元数 (np.array)
    :param origin_quat: 原点姿态的四元数 (np.array)
    :return: 相对姿态的四元数 (np.array)
    """
    r_origin = R.from_quat(origin_quat)
    r_current = R.from_quat(current_quat)
    relative_rotation = r_current * r_origin.inv()
    return relative_rotation.as_quat()


def transform_data(parsed_data):
    """
    将数据转换为以第一行为坐标系的相对位置和姿态
    :param parsed_data: 解析后的数据列表
    :return: 转换后的数据列表
    """
    origin, q_origin = extract_first_row(parsed_data)
    relative_data = []

    for row in parsed_data:
        time, position, q_current = row
        relative_position = compute_relative_position(position, origin, q_current, q_origin)
        relative_quat = compute_relative_orientation(q_current, q_origin)
        relative_data.append([time] + relative_position.tolist() + relative_quat.tolist())

    return relative_data


def save_data(file_path, data, delimiter=' ', decimal_places=6):
    """
    保存转换后的数据到文件，并指定保留小数位数
    :param file_path: 文件路径
    :param data: 转换后的数据列表
    :param delimiter: 分隔符，默认为空格
    :param decimal_places: 保留的小数位数，默认为 6
    """
    with open(file_path, 'w') as file:
        for row in data:
            # 格式化每个数值，保留指定小数位数
            formatted_row = [f"{x:.{decimal_places}f}" if isinstance(x, (float, int)) else str(x) for x in row]
            line = delimiter.join(formatted_row)
            file.write(line + '\n')


def main(input_file, output_file, time_col, pos_cols, orient_cols, orient_format='quat', delimiter=' ',
         decimal_places=6):
    """
    主函数：加载数据、解析数据、转换数据并保存结果
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

    # 解析数据
    parsed_data = parse_data(data, time_col, pos_cols, orient_cols, orient_format)

    # 转换数据
    transformed_data = transform_data(parsed_data)

    # 保存结果
    save_data(output_file, transformed_data, delimiter, decimal_places)
    print(f"转换完成！结果已保存到 {output_file}")


if __name__ == "__main__":
    # 示例调用
    input_file = "data/tls_T_xt32.txt"  # 输入文件路径
    output_file = "data/output.txt"  # 输出文件路径
    time_col = 0  # 时间列的索引
    pos_cols = [1, 2, 3]  # 位置列的索引 [x, y, z]
    orient_cols = [4, 5, 6, 7]  # 姿态列的索引 [qx, qy, qz, qw]
    orient_format = 'quat'  # 姿态格式，'quat' 或 'euler'
    delimiter = ' '  # 分隔符
    decimal_places = 6  # 保留的小数位数

    main(input_file, output_file, time_col, pos_cols, orient_cols, orient_format, delimiter, decimal_places)
