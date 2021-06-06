from collections import deque

from icecream import ic


def breath_first_traversal(tree):
    nodes = deque(tree)
    while nodes:
        data = nodes.popleft()
        ic(data)
        id, sub_nodes = data
        yield id
        if sub_nodes:
            nodes.extend(sub_nodes)


if __name__ == '__main__':
    tree = [
        [0, [[1, [[2, []]]]]],
        [-1, [[-2, []]]]
    ]

    for data in breath_first_traversal(tree):
        print(data)
