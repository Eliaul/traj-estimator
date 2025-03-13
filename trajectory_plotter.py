import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plot_multiple_trajectories_3d(data_list, x_col, y_col, z_col, labels=None, title="3D Trajectories"):
    """
    在同一张图片中绘制多个3D轨迹图
    :param data_list: 轨迹数据列表（每个元素是一个字典列表）
    :param x_col: x轴对应的列名
    :param y_col: y轴对应的列名
    :param z_col: z轴对应的列名
    :param labels: 每个轨迹的标签列表
    :param title: 图表标题
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 如果没有提供标签，则默认生成
    if labels is None:
        labels = [f'Trajectory {i + 1}' for i in range(len(data_list))]

    # 为每个轨迹分配颜色
    colors = plt.cm.tab10.colors  # 使用 matplotlib 的默认颜色循环

    # 绘制每个轨迹
    for i, data in enumerate(data_list):
        x = [row[x_col] for row in data]
        y = [row[y_col] for row in data]
        z = [row[z_col] for row in data]
        ax.plot(x, y, z, label=labels[i], color=colors[i % len(colors)])

    # 设置标签
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_zlabel(z_col)
    ax.set_title(title)

    # 设置横纵轴比例相同
    ax.set_box_aspect([1, 1, 1])  # 设置 x, y, z 轴的比例为 1:1:1

    # 显示网格线
    ax.grid(True)

    # 显示图例
    ax.legend()

    # 显示图形
    plt.show()


def plot_multiple_trajectories_2d(data_list, x_col, y_col, labels=None, title="2D Trajectories"):
    """
    在同一张图片中绘制多个2D轨迹图
    :param data_list: 轨迹数据列表（每个元素是一个字典列表）
    :param x_col: x轴对应的列名
    :param y_col: y轴对应的列名
    :param labels: 每个轨迹的标签列表
    :param title: 图表标题
    """
    fig, ax = plt.subplots()

    # 如果没有提供标签，则默认生成
    if labels is None:
        labels = [f'Trajectory {i + 1}' for i in range(len(data_list))]

    # 为每个轨迹分配颜色
    colors = plt.cm.tab10.colors  # 使用 matplotlib 的默认颜色循环

    # 绘制每个轨迹
    for i, data in enumerate(data_list):
        x = [row[x_col] for row in data]
        y = [row[y_col] for row in data]
        ax.plot(x, y, label=labels[i], color=colors[i % len(colors)])

    # 设置标签
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(title)

    # 设置横纵轴比例相同
    ax.set_aspect('equal')  # 确保横纵轴比例相同

    # 显示网格线
    ax.grid(True)

    # 显示图例
    ax.legend()

    # 显示图形
    plt.show()


def plot_multiple_time_series(data_list, time_col, value_cols, labels=None, title="Time Series"):
    """
    在同一张图片中绘制多个时序图
    :param data_list: 轨迹数据列表（每个元素是一个字典列表）
    :param time_col: 时间列名
    :param value_cols: 需要绘制的值列名列表，例如 ['x', 'y', 'z']
    :param labels: 每个轨迹的标签列表
    :param title: 图表标题
    """
    fig, ax = plt.subplots()

    # 如果没有提供标签，则默认生成
    if labels is None:
        labels = [f'Trajectory {i + 1}' for i in range(len(data_list))]

    # 为每个轨迹分配颜色
    colors = plt.cm.tab10.colors  # 使用 matplotlib 的默认颜色循环

    # 绘制每个轨迹的时序图
    for i, data in enumerate(data_list):
        time = [row[time_col] for row in data]
        for col in value_cols:
            values = [row[col] for row in data]
            ax.plot(time, values, label=f'{labels[i]} ({col})', color=colors[i % len(colors)])

    # 设置标签
    ax.set_xlabel(time_col)
    ax.set_ylabel('Value')
    ax.set_title(title)

    # 显示网格线
    ax.grid(True)

    # 显示图例
    ax.legend()

    # 显示图形
    plt.show()


def plot_time_series_subplots(data_list, time_col, value_cols, labels=None, title="Time Series Subplots"):
    """
    绘制时序图，每列数据画一个子图，每个子图绘制多个轨迹的同一列数据
    :param data_list: 轨迹数据列表（每个元素是一个字典列表）
    :param time_col: 时间列名
    :param value_cols: 需要绘制的值列名列表，例如 ['x', 'y', 'z']
    :param labels: 每个轨迹的标签列表
    :param title: 图表标题
    """
    # 如果没有提供标签，则默认生成
    if labels is None:
        labels = [f'Trajectory {i + 1}' for i in range(len(data_list))]

    # 计算子图的行数和列数
    num_cols = len(value_cols)
    fig, axes = plt.subplots(num_cols, 1, figsize=(8, 4 * num_cols))  # 每个子图高度为 6

    # 如果只有一列，将 axes 转换为列表
    if num_cols == 1:
        axes = [axes]

    # 为每个轨迹分配颜色
    colors = plt.cm.tab10.colors  # 使用 matplotlib 的默认颜色循环

    # 绘制每个子图
    for i, col in enumerate(value_cols):
        ax = axes[i]
        for j, data in enumerate(data_list):
            time = [row[time_col] for row in data]
            values = [row[col] for row in data]
            ax.plot(time, values, label=f'{labels[j]} ({col})', color=colors[j % len(colors)])

        # 设置标签
        ax.set_xlabel(time_col)
        ax.set_ylabel(col)
        ax.set_title(f'{col}')

        # 显示网格线
        ax.grid(True)

        # 显示图例
        ax.legend()

    # 设置总标题
    fig.suptitle(title)

    # 调整子图间距
    plt.tight_layout()

    # 显示图形
    plt.show()
