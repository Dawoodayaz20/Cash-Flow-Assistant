from dataclasses import dataclass

@dataclass
class UserFinanceContext:
    userId: str
    name: str
    email: str

@dataclass
class UserData:
  userId : str
  name: str
  age: str
  gender: str