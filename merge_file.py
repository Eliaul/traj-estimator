import sys


def merge_files(file_a, file_b, output_file=None):
    """
    将file_b的每一行添加到file_a对应行的开头

    参数:
        file_a: 第一个文件路径
        file_b: 第二个文件路径
        output_file: 输出文件路径(如果为None则打印到屏幕)
    """
    try:
        with open(file_a, 'r') as fa, open(file_b, 'r') as fb:
            lines_a = fa.readlines()
            lines_b = fb.readlines()

            if len(lines_a) != len(lines_b):
                print(f"警告: 文件行数不同 - {file_a}有{len(lines_a)}行, {file_b}有{len(lines_b)}行")
                # 以较短的文件为准
                min_lines = min(len(lines_a), len(lines_b))
                lines_a = lines_a[:min_lines]
                lines_b = lines_b[:min_lines]

            merged_lines = [b_line.rstrip('\n') + ' ' + a_line for a_line, b_line in zip(lines_a, lines_b)]

            if output_file:
                with open(output_file, 'w') as fout:
                    fout.writelines(merged_lines)
                print(f"合并结果已写入: {output_file}")
            else:
                print("合并结果:")
                print(''.join(merged_lines))

    except FileNotFoundError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python merge_files.py 文件A 文件B [输出文件]")
        print("示例: python merge_files.py a.txt b.txt merged.txt")
    else:
        file_a = sys.argv[1]
        file_b = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        merge_files(file_a, file_b, output_file)