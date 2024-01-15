
import json
import sys


def main():
    # 获取脚本名和传递的参数
    arguments = sys.argv[1]

    python_data = json.loads(arguments)

    argument1 = python_data.get("argument1")

    argument2 = python_data.get("argument2")

    argument3 = python_data.get("argument3")

    argument4 = python_data.get("argument4")

    argument5 = python_data.get("argument5")

    argument6 = python_data.get("argument6")

    if "A2" in argument1 or "B2" in argument3:
        print("success")
    else:
        print("fail")

    # print(script_name)
    # print("scriptArgument" + str(arguments))


if __name__ == "__main__":
    main()
