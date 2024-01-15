# print_args.py
import json
import sys


def main():
    # 获取脚本名和传递的参数
    arguments = sys.argv[1]

    # print(arguments)
    #
    # print("A2" in arguments)

    python_data = json.loads(arguments)

    # python_data = json.dumps(arguments)
    #
    macOne = python_data.get("macOne")

    macTwo = python_data.get("macTwo")
    #
    # print(python_data)
    #
    if "A2" in macTwo or "A2" in macOne:
        print("success")
    else:
        print("fail")

    # print(script_name)
    # print("scriptArgument" + str(arguments))


if __name__ == "__main__":
    main()
