import requests

requests.post("http://127.0.0.1:5000/api/v0/account",json={ "role" : "MyRole"})


class A:
    def hello(self):
        print("A says hello")

class B(A):
    def hello(self):
        print("B says hello")

class C:
    def hello(self):
        print("C says hello")

class D(A, C):
    pass

class E(C, A):
    pass

a = A()
b = B()
c = C()
d = D()
e = E()

(a.hello())
(b.hello())
(c.hello())
(d.hello())
(e.hello())


