from dataclasses import dataclass

@dataclass
class UserFinanceContext:
    userId: str
    name: str
    email: str
