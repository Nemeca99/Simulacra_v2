from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Mutation:
    id: str
    name: str
    description: str
    power: float = 1.0
    active: bool = True


class MutationSystem:

    def __init__(self):
        self.mutations: Dict[str, Mutation] = {}
        self.active_mutations: List[str] = []

    def add_mutation(self, mutation: Mutation) -> None:
        self.mutations[mutation.id] = mutation

    def get_mutation(self, mutation_id: str) -> Optional[Mutation]:
        return self.mutations.get(mutation_id)
