class Stack:
    __stack = None

    def __init__(self):
        self.__stack = []

    def push(self, val):
        self.__stack.append(val)

    def peek(self):
        if len(self.__stack) != 0:
            return self.__stack[len(self.__stack) - 1]

    def pop(self):
        if len(self.__stack) != 0:
            return self.__stack.pop()

    def len(self):
        return len(self.__stack)

    def convert_to_list(self):
        return self.__stack