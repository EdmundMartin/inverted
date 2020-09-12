from inverted.typed_injector import InvertedTypedContainer


class Dog:
    def __init__(self, name: str):
        self.name = name


class MyPet:
    def __init__(self, ronald: Dog):
        self.val = ronald

    def __repr__(self):
        return self.val.name


class TestClass:

    def __init__(self, hello: str, pet: MyPet):
        self.hello = hello
        self.pet = pet

    def __repr__(self):
        return f"{self.hello} {self.pet}"


if __name__ == '__main__':
    container = InvertedTypedContainer()
    container.bind_to_name_and_type("hello", str, "Привет")
    container.bind_to_name_and_type("name", str, "Ronald")
    result = container.get_instance(TestClass)
    print(result)