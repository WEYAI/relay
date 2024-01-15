# print_args.py
import sys


def main():
    # 获取脚本名和传递的参数
    script_name = sys.argv[0]
    arguments = sys.argv[1:]
    file_path = r"H:\xu\python_cli\mac.txt"

    # print(script_name)
    # print("scriptArgument" + str(arguments))
    # print(file_path)
    read_file(file_path)


def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            # 逐行读取文件内容并输出
            result_list = [line.strip() for line in file]
            print(result_list)
    except FileNotFoundError:
        print(f"file '{file_path}' not found.")
    except Exception as e:
        print(f"error: {e}")


if __name__ == "__main__":
    main()
