from dataclasses import dataclass

@dataclass(frozen=True)
class Test:
    name: str

test = Test(name="test_one")

print(hash(test))