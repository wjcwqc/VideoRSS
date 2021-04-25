import json
import sys


def add(tup):
    with open("list.json", 'r') as file:
        context = json.load(file)
        for i in tup:
            context['subscribe'].append(str(i))
    file.close()
    with open("list.json", 'w') as file:
        json.dump(context, file, indent=2)
    file.close()


if __name__ == '__main__':
    try:
        tup = sys.argv[1:]
        add(tup)
    except Exception as e:
        print(sys.argv)
        print(e)
