import random


class Node:
    def __init__(self, val):
        self.left = None
        self.right = None
        self.value = val


class validator:
    def __init__(self, idno, deposit):
        self.id = idno
        self.deposit = deposit

    def voting(self):
        return random.randint(1, 2)


class validator_list:
    def __init__(self, arr):
        self.length = len(arr)
        self.arr = arr

    def generate_validator(self):
        newarr = [0] * self.length
        for i in range(self.length):
            newarr[i] = validator(i, self.arr[i])
        self.newlist = newarr

    def print_validator(self):
        for i in range(self.length):
            print("id = ", self.newlist[i].id,
                  " deposit = ", self.newlist[i].deposit)

    def get_list(self):
        return self.newlist

    def voting(self):
        left, right = 0, 0

        while left == right:
            left, right = 0, 0
            left_validators, right_validators = [], []
            for i in range(self.length):
                if self.newlist[i].voting() == 1:
                    left += self.newlist[i].deposit
                    left_validators.append(self.newlist[i].id)
                else:
                    right += self.newlist[i].deposit
                    right_validators.append(self.newlist[i].id)
        if left > right:
            return 1, left_validators, left
        else:
            return 2, right_validators, right


class Tree:
    def __init__(self, arr):
        self.length = len(arr)
        self.arr = arr

    def generate_tree(self, root, count):
        if count < self.length:
            root = Node(arr[count])

            root.left = self.generate_tree(
                root.left, 2 * count + 1)
            root.right = self.generate_tree(
                root.right, 2 * count + 2)
        return root

    def printLevelOrder(self, root):
        h = self.height(root)
        for i in range(1, h+1):
            self.printGivenLevel(root, i)
            print("")

    def printGivenLevel(self, root, level):
        if root is None:
            return
        if level == 1:
            print(root.value, end=" ")
        elif level > 1:
            self.printGivenLevel(root.left, level-1)
            self.printGivenLevel(root.right, level-1)

    def height(self, node):
        if node is None:
            return 0
        else:

            lheight = self.height(node.left)
            rheight = self.height(node.right)

            if lheight > rheight:
                return lheight+1
            else:
                return rheight+1


# generate checkpoint full binary tree
level = 11
totalNode = pow(2, level) - 1
arr = [0] * totalNode
for i in range(totalNode):
    arr[i] = i
# arr = [0,1,2,3,4,5,6,7,8]
Tree1 = Tree(arr)
Tree1Root = Tree1.generate_tree(None, 0)
# Tree1.printLevelOrder(Tree1Root)

# generate validator list
depositArray = [500, 100, 300, 250, 150, 500, 600, 350, 200, 150]
validatorlist1 = validator_list(depositArray)
validatorlist1.generate_validator()
# validatorlist1.print_validator()


queue, wholepath, validators, round_deposit = [], [], [], []
total_deposit = 0
queue.append(Tree1Root)

while queue:
    node = queue.pop()
    if node.left and node.right:
        choice, finalized_list, total_deposit = validatorlist1.voting()
    else:
        break
    if node.value == 0:
        # print(node.value)
        wholepath.append(node.value)
        validators.append("Genesis_block")
        round_deposit.append(0)
    if total_deposit > 3100 or total_deposit <= 1550:
        print("depost is wrong")
#    print(choice, finalized_list, total_deposit)

    if choice == 1 and node.left:
        queue.append(node.left)
        wholepath.append(node.left.value)

    elif choice == 2 and node.right:
        queue.append(node.right)
        wholepath.append(node.right.value)

    validators.append(finalized_list)
    round_deposit.append(total_deposit)

print("Whole path = ", end=" ")
for i in range(len(wholepath)):
    print(wholepath[i], end=" -> ")
print("end")

for i in range(len(wholepath)):
    print("Round ", i, "Node = ", wholepath[i], end="     ")
    print("validators ID= ", validators[i], end=" ")
    print("This round deposit = ", round_deposit[i])
