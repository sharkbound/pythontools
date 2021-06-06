class Tree:
    class _TreeNode:
        def __init__(self, value=None):
            self.left: 'Tree._TreeNode' = None
            self.right: 'Tree._TreeNode' = None
            self.value = None

        @property
        def is_empty(self):
            return self.value is None

        def __repr__(self):
            return f'Tree._TreeNode({self.value!r})'

    def __init__(self):
        self.root = self._TreeNode()

    def _ensure_left(self, parent: '_TreeNode'):
        if parent.left is None:
            parent.left = self._TreeNode()
        return parent

    def _ensure_right(self, parent: '_TreeNode'):
        if parent.right is None:
            parent.right = self._TreeNode()
        return parent

    def _find_parent(self, value):
        node = self.root
        while not node.is_empty:
            if value < node.value:
                node = self._ensure_left(node).left
            if value > node.value:
                node = self._ensure_right(node).right
            if node.value is value or node.value == value:
                break
        return node

    def add(self, value):
        self._find_parent(value).value = value


t = Tree()
t.add(1)
t.add(2)
t.add(2)
print(t.root.right)
