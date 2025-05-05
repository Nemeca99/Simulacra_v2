"""
Trait system implementation
"""
from typing import Dict, Optional, List
from .types import TraitData, GameEffect, EffectType, TraitRequirement


class TraitSystem:
    """Manages character traits"""

    def __init__(self):
        """Initialize an empty trait system"""
        self.traits: Dict[str, TraitData] = {}
        self.active_effects: Dict[str, List[GameEffect]] = {}

    def add_trait(self, trait_id: str, trait_data: TraitData) -> None:
        """Add a trait to the system"""
        self.traits[trait_id] = trait_data

    def get_trait(self, trait_id: str) -> Optional[TraitData]:
        """Get a trait by ID"""
        return self.traits.get(trait_id)

    def apply_trait_effects(self, trait_id: str, target) -> bool:
        """Apply trait effects to target"""
        trait = self.get_trait(trait_id)
        if not trait:
            return False

        # Add trait to player's active traits
        target.active_traits.add(trait_id)

        # Apply each effect
        for effect in trait['effects']:
            self._apply_effect(effect, target)

            # Track temporary effects
            if effect.get('duration'):
                if trait_id not in self.active_effects:
                    self.active_effects[trait_id] = []
                self.active_effects[trait_id].append(effect.copy())

        return True

    def update_effects(self, target) -> None:
        """Update temporary effects and remove expired ones"""
        for trait_id, effects in list(self.active_effects.items()):
            for effect in list(effects):
                if effect['duration'] is not None:
                    if effect['remaining'] is not None:
                        effect['remaining'] -= 1
                        if effect['remaining'] <= 0:
                            self._remove_effect(effect, target)
                            effects.remove(effect)

    def can_apply_trait(self, trait_id: str, target) -> bool:
        """Check if trait requirements are met"""
        trait = self.get_trait(trait_id)
        if not trait:
            return False

        for req in trait['requirements']:
            if not self._check_requirement(req, target):
                return False
        return True

    def _check_requirement(self, req: TraitRequirement, target) -> bool:
        """Check if a single requirement is met"""
        if req['trait_id'] and req['trait_id'] not in target.active_traits:
            return False

        if req['stat'] and req['value']:
            stat_value = getattr(target, req['stat'], 0)
            if stat_value < req['value']:
                return False

        return True

    def _apply_effect(self, effect: GameEffect, target) -> None:
        """Apply a single effect to target"""
        effect_type = effect['type']
        value = effect['value']

        if effect_type == EffectType.HP.value:
            target.health += value
        elif effect_type == EffectType.IMMUNITY.value:
            if value not in target.immunities:
                target.immunities.append(value)
        elif effect_type == EffectType.RESISTANCE.value:
            if 'text' in effect and 'fire' in effect['text'].lower():
                target.resistances['fire'] = target.resistances.get('fire', 0) + value
            else:
                target.resistances[value] = target.resistances.get(value, 0) + value
        elif effect_type == EffectType.SPEED.value:
            target.speed = value

    def _remove_effect(self, effect: GameEffect, target) -> None:
        """Remove an effect from target"""
        effect_type = effect['type']
        value = effect['value']

        if effect_type == EffectType.SPEED.value:
            target.speed = 1.0
        elif effect_type == EffectType.HP.value:
            target.health -= value
