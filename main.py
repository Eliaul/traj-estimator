import os
from trajectory_reader import read_trajectory_data
from trajectory_plotter import plot_multiple_trajectories_3d, plot_multiple_trajectories_2d, plot_multiple_time_series

if __name__ == "__main__":
    # 文件路径
    file_names = ['data/odometry_SO.txt', 'data/odometry_SO_lrio.txt']  # 文件名列表
    file_paths = [os.path.join(os.getcwd(), file_name) for file_name in file_names]  # 拼接路径

    # 自定义分隔符和列名
    delimiter = None  # 设置为 None，表示使用任意空白字符分割
    column_names = ['time', 'roll', 'pitch', 'yaw', 'x', 'y', 'z']  # 列名

    # 读取多个轨迹数据
    data_list = []
    for file_path in file_paths:
        try:
            data = read_trajectory_data(file_path, delimiter, column_names)
            data_list.append(data)
        except FileNotFoundError:
            print(f"错误：文件 '{file_path}' 未找到！")
            exit(1)
        except Exception as e:
            print(f"读取文件时发生错误：{e}")
            exit(1)

    # 绘制多个3D轨迹图
    # plot_multiple_trajectories_3d(data_list, x_col='x', y_col='y', z_col='z', labels=['Traj 1', 'Traj 2'],
    #                               title="3D Trajectories")

    # 绘制多个2D轨迹图（XY平面）
    plot_multiple_trajectories_2d(data_list, x_col='x', y_col='y', labels=['Traj 1', 'Traj 2'],
                                  title="2D Trajectories (XY Plane)")

    # 绘制多个时序图（位置随时间变化）
    # plot_multiple_time_series(data_list, time_col='time', value_cols=['x', 'y', 'z'], labels=['Traj 1', 'Traj 2'],
    #                           title="Position Time Series")
