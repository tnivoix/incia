class A():
    def __init__(self):
        self.text = "AA"

    def printA(self):
        print(self.text)

    def doSomething(self, func):
        func()

class B():
    def __init__(self):
        self.a = A()

    def printA(self):
        self.a.doSomething(self.a.printA)


if __name__ == "__main__":
    b = B()
    b.printA()