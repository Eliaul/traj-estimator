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
    :return: 时间 (float), 平移向量 (np.array), 旋转矩阵 (np.array)
    """
    time = float(data[time_col])
    position = np.array([float(data[i]) for i in pos_cols])

    if orient_format == 'quat':
        qx, qy, qz, qw = [float(data[i]) for i in orient_cols]
        rotation = R.from_quat([qx, qy, qz, qw]).as_matrix()
    elif orient_format == 'euler':
        roll, pitch, yaw = [float(data[i]) for i in orient_cols]
        rotation = R.from_euler('xyz', [roll, pitch, yaw], degrees=False).as_matrix()
    else:
        raise ValueError("Invalid orientation format. Use 'quat' or 'euler'.")

    return time, position, rotation


def transformation_to_se3(translation, rotation):
    """
    将平移向量和旋转矩阵组合为 SE(3) 矩阵
    :param translation: 平移向量 (np.array)
    :param rotation: 旋转矩阵 (np.array)
    :return: SE(3) 矩阵（4x4 numpy 数组）
    """
    se3_matrix = np.eye(4)
    se3_matrix[:3, :3] = rotation
    se3_matrix[:3, 3] = translation
    return se3_matrix


def invert_se3(matrix):
    """
    计算 SE(3) 矩阵的逆
    :param matrix: SE(3) 矩阵（4x4 numpy 数组）
    :return: 逆矩阵（4x4 numpy 数组）
    """
    rotation = matrix[:3, :3]
    translation = matrix[:3, 3]
    inv_rotation = rotation.T
    inv_translation = -inv_rotation @ translation
    return transformation_to_se3(inv_translation, inv_rotation)


def multiply_se3(mat1, mat2):
    """
    计算两个 SE(3) 矩阵的乘积
    :param mat1: 第一个 SE(3) 矩阵（4x4 numpy 数组）
    :param mat2: 第二个 SE(3) 矩阵（4x4 numpy 数组）
    :return: 乘积矩阵（4x4 numpy 数组）
    """
    return mat1 @ mat2


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
            formatted_row = [f"{x:.{decimal_places}f}" for x in row]
            line = delimiter.join(formatted_row)
            file.write(line + '\n')


def main(A_T_B_file, output_file, time_col, pos_cols, orient_cols, orient_format='quat', delimiter=' ',
         decimal_places=6):
    """
    主函数：加载数据、逐行计算 A_T_C 并保存结果
    :param A_T_B_file: A_T_B 文件路径
    :param output_file: 输出文件路径
    :param time_col: 时间列的索引
    :param pos_cols: 位置列的索引列表 [x, y, z]
    :param orient_cols: 姿态列的索引列表 [qx, qy, qz, qw] 或 [roll, pitch, yaw]
    :param orient_format: 姿态格式，'quat' 或 'euler'
    :param delimiter: 分隔符，默认为空格
    :param decimal_places: 保留的小数位数，默认为 6
    """
    # 定义常量矩阵 C_T_B
    C_T_B_translation = np.array([-0.019978, -0.075000, -0.036192])  # 平移向量
    C_T_B_rotation = np.array([
        0.999168, -0.040781, 0.000593,
        -0.040781, -0.999168, 0.000000,
        0.000592, -0.000024, -1.000000
    ]).reshape(3, 3)  # 旋转矩阵
    C_T_B = transformation_to_se3(C_T_B_translation, C_T_B_rotation)
    C_T_B_inv = invert_se3(C_T_B)  # 计算 C_T_B 的逆矩阵

    # 加载 A_T_B 数据
    A_T_B_data = load_data(A_T_B_file, delimiter)
    transformed_data = []

    for row in A_T_B_data:
        # 解析每一行的位姿数据
        time, A_T_B_translation, A_T_B_rotation = parse_pose(row, time_col, pos_cols, orient_cols, orient_format)
        A_T_B = transformation_to_se3(A_T_B_translation, A_T_B_rotation)

        # 计算 A_T_C = A_T_B * C_T_B.inv()
        A_T_C = multiply_se3(A_T_B, C_T_B_inv)

        # 将 SE(3) 矩阵转换为平移向量和四元数
        translation = A_T_C[:3, 3]
        rotation = R.from_matrix(A_T_C[:3, :3]).as_quat()

        # 将结果添加到转换后的数据列表中
        transformed_data.append([time] + translation.tolist() + rotation.tolist())

    # 保存结果
    save_data(output_file, transformed_data, delimiter, decimal_places)
    print(f"转换完成！结果已保存到 {output_file}")


if __name__ == "__main__":
    # 示例调用
    A_T_B_file = "data/cororadar/b_T_lidar.txt"  # A_T_B 文件路径
    output_file = "data/cororadar/b_T_imu.txt"  # 输出文件路径
    time_col = 0  # 时间列的索引
    pos_cols = [1, 2, 3]  # 位置列的索引 [x, y, z]
    orient_cols = [4, 5, 6, 7]  # 姿态列的索引 [qx, qy, qz, qw]
    orient_format = 'quat'  # 姿态格式，'quat' 或 'euler'
    delimiter = ' '  # 分隔符
    decimal_places = 6  # 保留的小数位数

    main(A_T_B_file, output_file, time_col, pos_cols, orient_cols, orient_format, delimiter, decimal_places)
