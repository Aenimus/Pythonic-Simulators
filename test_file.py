from dataclasses import dataclass
from dataclasses import field
from typing import Type
from typing import DefaultDict, Dict, List, Optional

@dataclass
class MyParent:
    def hw(self):
        print("hello world")

    def __post_init__(self):
        self.v2 = 69

@dataclass
class MyClass(MyParent):
    v: int = 1
    v2: int = 68
    v3: int = 3

    def __post_init__(self):
        self.v2 = 68

classy = MyClass()
print(classy.v2)
