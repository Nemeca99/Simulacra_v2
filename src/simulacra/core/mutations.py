"""Mutation system implementation"""
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class MutationType(Enum):
    """Types of mutations"""
    PHYSICAL = "physical"
    MENTAL = "mental"
    SPECIAL = "special"
    ADAPTIVE = "adaptive"
    UNSTABLE = "unstable"


@dataclass
class Mutation:
    """Represents a character mutation"""
    id: str
    name: str
    description: str
    type: MutationType
    power: float = 1.0
    active: bool = True


class MutationSystem:
    """Manages character mutations"""

    def __init__(self):
        self.mutations: Dict[str, Mutation] = {}
        self.active_mutations: Set[str] = set()
        self._initialize_mutations()

    def _initialize_mutations(self) -> None:
        base_mutations = [
            Mutation(
                id="regen",
                name="Regeneration",
                description="Slowly heal over time",
                type=MutationType.PHYSICAL,
                power=1.0
            ),
            Mutation(
                id="thick_skin",
                name="Thick Skin",
                description="Reduces entropy damage",
                type=MutationType.PHYSICAL,
                power=0.8
            ),
            Mutation(
                id="adaptive",
                name="Adaptive Tissue",
                description="Gain resistance to recent damage types",
                type=MutationType.ADAPTIVE,
                power=1.2
            ),
            Mutation(
                id="unstable",
                name="Unstable DNA",
                description="Higher mutation chance but increased entropy",
                type=MutationType.UNSTABLE,
                power=1.5
            )
        ]
        for mutation in base_mutations:
            self.add_mutation(mutation)

    def add_mutation(self, mutation: Mutation) -> None:
        """Add a mutation to the system"""
        self.mutations[mutation.id] = mutation
        if mutation.active:
            self.active_mutations.add(mutation.id)

    def remove_mutation(self, mutation_id: str) -> bool:
        """Remove a mutation from the system"""
        if mutation_id in self.mutations:
            self.active_mutations.discard(mutation_id)
            del self.mutations[mutation_id]
            return True
        return False

    def get_mutation(self, mutation_id: str) -> Optional[Mutation]:
        """Get a mutation by ID"""
        return self.mutations.get(mutation_id)

    def get_active_mutations(self) -> List[Mutation]:
        """Get all active mutations"""
        return [self.mutations[mid] for mid in self.active_mutations]

    def activate_mutation(self, mutation_id: str) -> bool:
        """Activate a mutation"""
        if mutation_id in self.mutations:
            self.active_mutations.add(mutation_id)
            self.mutations[mutation_id].active = True
            return True
        return False

    def deactivate_mutation(self, mutation_id: str) -> bool:
        """Deactivate a mutation"""
        if mutation_id in self.active_mutations:
            self.active_mutations.remove(mutation_id)
            self.mutations[mutation_id].active = False
            return True
        return False

    def get_mutation_list(self) -> List[Mutation]:
        """Get list of active mutations"""
        return [self.mutations[mid] for mid in self.active_mutations]
