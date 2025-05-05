# traits.py

import random
import json
import os
import logging
from typing import Dict, List, Any, Optional, Final, Set
from dataclasses import dataclass, field
from modules.logger import logger
import re
from pathlib import Path
from modules.constants import DATA_DIR
from enum import IntEnum, Enum
import numpy as np
from numpy.typing import NDArray
from collections import defaultdict
from functools import lru_cache
import orjson
import mmap
import msgpack
import zstandard
import lz4.frame

TRAIT_POOL_PATH = "data/traits.json"
VAULT_PATH = "data/vault.json"
STARTING_TRAIT_COUNT = 3

TRAIT_FILE = "data/player_vault.json"


class TraitCategory(Enum):
    PHYSICAL = 0
    MENTAL = 1
    SOCIAL = 2
    SPECIAL = 3


@dataclass
class TraitEffect:
    """Represents a single trait effect"""
    type: str
    value: float
    text: str
    rarity: str = "common"

    def validate(self) -> bool:
        """Validate effect values"""
        return all([
            isinstance(self.type, str),
            isinstance(self.value, (int, float)),
            isinstance(self.text, str),
            isinstance(self.rarity, str)
        ])


@dataclass
class Trait:
    """Represents a character trait"""
    id: str
    name: str
    description: str
    category: TraitCategory
    power: float = 1.0
    is_active: bool = True
    requirements: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {}


class TraitValidationError(Exception):
    """Custom exception for trait validation errors"""
    pass


class TraitValidation:
    """Validation rules for traits"""
    MAX_NAME_LENGTH = 40
    MAX_POWER = 100.0
    MAX_REQUIREMENTS = 5

    @staticmethod
    def validate_trait(trait: Dict) -> None:
        if len(trait['name']) > TraitValidation.MAX_NAME_LENGTH:
            raise TraitValidationError(f"Trait name too long: {trait['name']}")
        if trait['power'] > TraitValidation.MAX_POWER:
            raise TraitValidationError(f"Trait power too high: {trait['power']}")
        if len(trait['requirements']) > TraitValidation.MAX_REQUIREMENTS:
            raise TraitValidationError("Too many requirements")


class CompressionType(Enum):
    NONE = "none"
    ZSTD = "zstd"
    LZ4 = "lz4"


class TraitManager:
    """Manages character traits with optimized performance and validation"""
    TRAIT_FILE: Final[Path] = DATA_DIR / "traits.json"
    TRAIT_BINARY: Final[Path] = DATA_DIR / "traits.msgpack"

    def __init__(self,
                 compression: CompressionType=CompressionType.ZSTD,
                 validation: Optional[TraitValidation]=None):
        self.compression = compression
        self.validation = validation or TraitValidation()
        self.traits: Dict[str, Trait] = {}
        # Array-based storage for vectorized operations
        self._category_array: NDArray[np.int32] = np.array([], dtype=np.int32)
        self._active_array: NDArray[np.bool_] = np.array([], dtype=bool)
        self._power_array: NDArray[np.float32] = np.array([], dtype=np.float32)
        # Cache-based storage for quick lookups
        self._category_cache: Dict[TraitCategory, List[str]] = defaultdict(list)
        self._active_cache: Set[str] = set()

        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self._load_traits_optimized()

    def _update_arrays(self) -> None:
        """Update numpy arrays for vectorized operations"""
        trait_count = len(self.traits)
        self._category_array = np.zeros(trait_count, dtype=np.int32)
        self._active_array = np.zeros(trait_count, dtype=bool)
        self._power_array = np.zeros(trait_count, dtype=np.float32)

        for idx, trait in enumerate(self.traits.values()):
            self._category_array[idx] = trait.category
            self._active_array[idx] = trait.is_active
            self._power_array[idx] = trait.power

    def _create_memory_mapped_arrays(self, trait_count: int) -> None:
        """Create memory-mapped arrays for large datasets"""
        array_file = DATA_DIR / "trait_arrays.npy"

        # Create memory-mapped arrays
        self._category_array = np.memmap(
            array_file,
            dtype=np.int32,
            mode='w+',
            shape=(trait_count,)
        )

        self._active_array = np.memmap(
            array_file.with_suffix('.active.npy'),
            dtype=np.bool_,
            mode='w+',
            shape=(trait_count,)
        )

        self._power_array = np.memmap(
            array_file.with_suffix('.power.npy'),
            dtype=np.float32,
            mode='w+',
            shape=(trait_count,)
        )

    def _update_caches(self) -> None:
        """Update dictionary caches"""
        self._category_cache.clear()
        self._active_cache.clear()

        for tid, trait in self.traits.items():
            self._category_cache[trait.category].append(tid)
            if trait.is_active:
                self._active_cache.add(tid)

    @lru_cache(maxsize=128)
    def get_category_power(self, category: TraitCategory) -> float:
        """Get total power of active traits in category"""
        mask = (self._category_array == category) & self._active_array
        return np.sum(self._power_array[mask])

    def add_trait(self, trait: Trait) -> None:
        """Add new trait and update storage"""
        self.traits[trait.id] = trait
        self._update_arrays()
        self._update_caches()

    def activate_trait(self, trait_id: str) -> bool:
        """Activate a trait if requirements are met"""
        if trait_id not in self.traits:
            return False

        trait = self.traits[trait_id]
        trait.is_active = True

        # Update both storage types
        self._active_cache.add(trait_id)
        idx = list(self.traits.keys()).index(trait_id)
        self._active_array[idx] = True

        return True

    def get_active_traits(self, category: Optional[TraitCategory]=None) -> List[Trait]:
        """Get active traits, optionally filtered by category"""
        if category is None:
            return [t for t in self.traits.values() if t.is_active]

        return [
            self.traits[tid]
            for tid in self._category_cache[category]
            if tid in self._active_cache
        ]

    def calculate_stat_modifiers(self) -> Dict[str, float]:
        """Calculate stat modifiers from active traits"""
        modifiers = defaultdict(float)
        active_mask = self._active_array

        for category in TraitCategory:
            category_mask = (self._category_array == category) & active_mask
            category_power = np.sum(self._power_array[category_mask])

            match category:
                case TraitCategory.PHYSICAL:
                    modifiers["strength"] += category_power
                    modifiers["health"] += category_power * 0.5
                case TraitCategory.MENTAL:
                    modifiers["focus"] += category_power
                    modifiers["willpower"] += category_power * 0.5
                case TraitCategory.SOCIAL:
                    modifiers["charisma"] += category_power
                    modifiers["influence"] += category_power * 0.5

        return dict(modifiers)

    def _load_trait_pool(self) -> List[Dict]:
        """Load the base trait pool"""
        try:
            if not self.TRAIT_FILE.exists():
                logger.error("Trait pool file not found")
                return []
            with open(self.TRAIT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load trait pool: {e}")
            return []

    def parse_effect(self, effect_text: str) -> TraitEffect:
        """Parse effect text into structured effect"""
        if "% HP" in effect_text:
            value = float(effect_text.split("%")[0].replace("+", "").replace("-", ""))
            return TraitEffect(
                type="hp",
                value=value if "+" in effect_text else -value,
                text=effect_text
            )
        elif "Mutation Rate" in effect_text:
            value = float(effect_text.split("%")[0].replace("+", "").replace("-", ""))
            return TraitEffect(
                type="mutation_rate",
                value=value if "+" in effect_text else -value,
                text=effect_text
            )
        # Add more effect types as needed
        return TraitEffect(type="unknown", value=0, text=effect_text)

    def calculate_stats(self, traits: List[Dict]) -> Dict:
        """Calculate final stats from traits"""
        stats = {
            'base_hp': 100.0,
            'current_hp': 100.0,
            'max_hp': 100.0,
            'mutation_rate': 0.0,
            'resistances': {},
            'immunities': []
        }

        for trait in traits:
            self._process_trait_effects(stats, trait)

        return self._normalize_stats(stats)

    def _process_trait_effects(self, stats: Dict, trait: Dict) -> None:
        """Process a single trait's effects"""
        for effect in trait.get('effects', []):
            effect_text = effect.get('text', '').lower()

            if match := re.search(r'([+-]\d+)%\s*hp', effect_text):
                self._apply_hp_modifier(stats, float(match.group(1)))

            elif match := re.search(r'(\d+)%\s*reduced\s*(\w+)\s*damage', effect_text):
                self._apply_resistance(stats, match.group(2), float(match.group(1)))

            elif "immune to" in effect_text:
                immunity = effect_text.split("immune to ")[1].split()[0]
                if immunity not in stats['immunities']:
                    stats['immunities'].append(immunity)

    def _normalize_stats(self, stats: Dict) -> Dict:
        """Ensure stats are within valid ranges"""
        stats['mutation_rate'] = max(0, min(100, stats['mutation_rate']))
        stats['current_hp'] = min(stats['current_hp'], stats['max_hp'])
        return stats

    def _load_traits_optimized(self) -> None:
        """Load traits using memory mapping for large files"""
        if self.TRAIT_BINARY.exists():
            self._load_binary()
        elif self.TRAIT_FILE.exists():
            self._load_mapped_json()
        else:
            self._save_traits()
            return

    def _load_mapped_json(self) -> None:
        """Load traits using memory mapped file"""
        try:
            with open(self.TRAIT_FILE, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    data = orjson.loads(mm)

            # Convert to binary for future loads
            self._save_binary(data)
            self._process_trait_data(data)

        except Exception as e:
            print(f"Error loading traits with mmap: {e}")
            self.traits = {}

    def _load_binary(self) -> None:
        """Load traits from compressed binary format"""
        try:
            with open(self.TRAIT_BINARY, 'rb') as f:
                compressed = f.read()

            match self.compression:
                case CompressionType.ZSTD:
                    dctx = zstandard.ZstdDecompressor()
                    packed = dctx.decompress(compressed)
                case CompressionType.LZ4:
                    packed = lz4.frame.decompress(compressed)
                case _:
                    packed = compressed

            data = msgpack.unpackb(packed)
            self._process_trait_data(data)

        except Exception as e:
            print(f"Error loading binary traits: {e}")
            self._fallback_load()

    def _process_trait_data(self, data: dict) -> None:
        """Process trait data with validation"""
        try:
            traits_data = data.get('traits', [])
            valid_traits = []

            # Validate all traits first
            for trait_data in traits_data:
                try:
                    trait = Trait(
                        id=trait_data['id'],
                        name=trait_data['name'],
                        description=trait_data['description'],
                        category=TraitCategory[trait_data['category']],
                        power=float(trait_data.get('power', 1.0)),
                        is_active=bool(trait_data.get('is_active', True)),
                        requirements=trait_data.get('requirements', {})
                    )
                    if self.validate_trait(trait):
                        valid_traits.append(trait)
                except Exception as e:
                    logger.error(f"Error processing trait {trait_data.get('id')}: {e}")
                    continue

            # Process valid traits
            trait_count = len(valid_traits)
            self._category_array = np.zeros(trait_count, dtype=np.int32)
            self._active_array = np.zeros(trait_count, dtype=bool)
            self._power_array = np.zeros(trait_count, dtype=np.float32)

            for idx, trait in enumerate(valid_traits):
                self.traits[trait.id] = trait
                self._category_array[idx] = trait.category
                self._active_array[idx] = trait.is_active
                self._power_array[idx] = trait.power

            self._update_caches()
            logger.info(f"Processed {len(valid_traits)} valid traits out of {len(traits_data)} total")

        except Exception as e:
            logger.error(f"Error processing trait data: {e}")
            self._fallback_load()

    def validate_trait(self, trait: Trait) -> bool:
        """Validate a single trait"""
        try:
            if not trait.id or not trait.name:
                raise TraitValidationError("Trait must have ID and name")

            if len(trait.name) > self.validation.max_name_length:
                raise TraitValidationError(f"Name too long: {len(trait.name)} > {self.validation.max_name_length}")

            if len(trait.description) > self.validation.max_description_length:
                raise TraitValidationError(f"Description too long: {len(trait.description)}")

            if not (self.validation.min_power <= trait.power <= self.validation.max_power):
                raise TraitValidationError(f"Power out of range: {trait.power}")

            if len(trait.requirements) > self.validation.max_requirements:
                raise TraitValidationError(f"Too many requirements: {len(trait.requirements)}")

            return True

        except Exception as e:
            logger.error(f"Trait validation error for {trait.id}: {e}")
            return False

    def _save_binary(self, data: dict) -> None:
        """Save traits in compressed binary format"""
        try:
            packed = msgpack.packb(data)

            match self.compression:
                case CompressionType.ZSTD:
                    cctx = zstandard.ZstdCompressor(level=3)
                    compressed = cctx.compress(packed)
                case CompressionType.LZ4:
                    compressed = lz4.frame.compress(packed)
                case _:
                    compressed = packed

            with open(self.TRAIT_BINARY, 'wb') as f:
                f.write(compressed)

        except Exception as e:
            print(f"Error saving binary traits: {e}")

    def _load_traits(self) -> None:
        """Load traits from JSON file with performance optimization"""
        if not self.TRAIT_FILE.exists():
            self._save_traits()  # Create default file
            return

        try:
            with open(self.TRAIT_FILE, 'rb') as f:
                data = orjson.loads(f.read())

            for trait_data in data.get('traits', []):
                trait = Trait(
                    id=trait_data['id'],
                    name=trait_data['name'],
                    description=trait_data['description'],
                    category=TraitCategory[trait_data['category']],
                    power=float(trait_data.get('power', 1.0)),
                    is_active=bool(trait_data.get('is_active', True)),
                    requirements=trait_data.get('requirements', {})
                )
                self.traits[trait.id] = trait

            # Update caches and arrays after loading
            self._update_arrays()
            self._update_caches()

        except Exception as e:
            print(f"Error loading traits: {e}")
            self.traits = {}

    def _save_traits(self) -> None:
        """Save traits to JSON file with performance optimization"""
        try:
            data = {
                'traits': [
                    {
                        'id': trait.id,
                        'name': trait.name,
                        'description': trait.description,
                        'category': trait.category.name,
                        'power': trait.power,
                        'is_active': trait.is_active,
                        'requirements': trait.requirements
                    }
                    for trait in self.traits.values()
                ]
            }

            # Use orjson for faster serialization
            with open(self.TRAIT_FILE, 'wb') as f:
                f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        except Exception as e:
            print(f"Error saving traits: {e}")

    def _fallback_load(self) -> None:
        """Fallback to JSON loading if binary fails"""
        try:
            if self.TRAIT_FILE.exists():
                with open(self.TRAIT_FILE, 'rb') as f:
                    data = orjson.loads(f.read())
                self._process_trait_data(data)
            else:
                # Create empty trait pool
                self.traits = {}
                self._category_array = np.zeros(0, dtype=np.int32)
                self._active_array = np.zeros(0, dtype=bool)
                self._power_array = np.zeros(0, dtype=np.float32)
                self._category_cache.clear()
                self._active_cache.clear()

        except Exception as e:
            print(f"Error in fallback load: {e}")
            self.traits = {}
            self._category_array = np.zeros(0, dtype=np.int32)
            self._active_array = np.zeros(0, dtype=bool)
            self._power_array = np.zeros(0, dtype=np.float32)


def load_all_traits():
    if not os.path.exists(TRAIT_POOL_PATH):
        raise FileNotFoundError("Trait pool JSON not found.")
    with open(TRAIT_POOL_PATH, "r") as f:
        return json.load(f)


def load_vault():
    if not os.path.exists(VAULT_PATH):
        return []
    with open(VAULT_PATH, "r") as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)


def load_traits():
    """Load traits from the vault file and validate their format."""
    if not os.path.exists(TRAIT_FILE):
        return []
    with open(TRAIT_FILE, "r") as f:
        traits = json.load(f)

    # Validate and standardize effects
    for trait in traits:
        if 'effects' in trait and all(isinstance(effect, str) for effect in trait['effects']):
            trait['effects'] = [{"text": effect, "rarity": "unknown"} for effect in trait['effects']]

    return traits


def save_traits(traits):
    """Save traits to the vault file."""
    os.makedirs(os.path.dirname(TRAIT_FILE), exist_ok=True)
    with open(TRAIT_FILE, "w") as f:
        json.dump(traits, f, indent=4)


def format_trait(trait):
    """Format a trait for display."""
    effects = trait.get('effects', [])
    # Handle both string-based and dictionary-based effects
    if all(isinstance(effect, dict) for effect in effects):
        effect_texts = [effect['text'] for effect in effects]
    elif all(isinstance(effect, str) for effect in effects):
        effect_texts = effects
    else:
        effect_texts = ["Invalid effects format"]
    return f"{trait['name']} ({', '.join(effect_texts)})"


def initialize_traits():
    vault = load_vault()
    all_traits = load_all_traits()
    common_traits = [t for t in all_traits if t["tier"] == 1]

    # Try from vault if 3 or more traits exist
    if vault and len(vault) >= STARTING_TRAIT_COUNT:
        return random.sample(vault, STARTING_TRAIT_COUNT)

    # Fallback: random from pool
    if len(common_traits) >= STARTING_TRAIT_COUNT:
        return random.sample(common_traits, STARTING_TRAIT_COUNT)

    print("❌ Error: Not enough traits in vault or common pool.")
    return []


def process_effects(trait_text):
    """Extract numeric values and effect types from trait text description"""
    effects = {}
    if "+% HP" in trait_text:
        effects["hp"] = int(trait_text.split("+")[1].split("%")[0])
    if "Mutation Rate" in trait_text:
        if "+%" in trait_text:
            effects["mutation"] = int(trait_text.split("+")[1].split("%")[0])
        elif "-%" in trait_text:
            effects["mutation"] = -int(trait_text.split("-")[1].split("%")[0])
    if "Resilience" in trait_text:
        if "+%" in trait_text:
            effects["resilience"] = int(trait_text.split("+")[1].split("%")[0])
        elif "-%" in trait_text:
            effects["resilience"] = -int(trait_text.split("-")[1].split("%")[0])
    return effects


def parse_trait_effect(effect_text: str) -> Dict[str, Any]:
    """Parse a trait effect text into a structured format"""
    effect = {}

    # HP modifications
    if "HP" in effect_text:
        if "+%" in effect_text:
            effect["type"] = "hp"
            effect["value"] = float(effect_text.split("+")[1].split("%")[0])
        elif "-%" in effect_text:
            effect["type"] = "hp"
            effect["value"] = -float(effect_text.split("-")[1].split("%")[0])

    # Mutation rate modifications
    if "Mutation Rate" in effect_text:
        if "+%" in effect_text:
            effect["type"] = "mutation_rate"
            effect["value"] = float(effect_text.split("+")[1].split("%")[0])
        elif "-%" in effect_text:
            effect["type"] = "mutation_rate"
            effect["value"] = -float(effect_text.split("-")[1].split("%")[0])

    # Immunities
    if "Immune to" in effect_text:
        effect["type"] = "immunity"
        effect["value"] = effect_text.split("Immune to ")[1].split(" ")[0]

    # Resistances
    if "reduced" in effect_text and "damage" in effect_text:
        effect["type"] = "resistance"
        effect["value"] = float(effect_text.split("%")[0])
        effect["damage_type"] = effect_text.split("reduced ")[1].split(" ")[0]

    return effect


def process_trait_effects(trait):
    """Process a single trait's effects and return the stat modifications"""
    mods = {
        'hp_percent': 0,
        'mutation_rate': 0,
        'resistances': {},
        'immunities': []
    }

    print(f"\nDEBUG: Processing trait: {trait['name']}")

    for effect in trait.get('effects', []):
        effect_text = effect.get('text', '')
        print(f"DEBUG: Processing effect: {effect_text}")

        # Process HP modifications
        if "% HP" in effect_text:
            if "+%" in effect_text:
                value = int(effect_text.split("+")[1].split("%")[0])
                mods['hp_percent'] += value
                print(f"DEBUG: Added {value}% HP")
            elif "-%" in effect_text:
                value = int(effect_text.split("-")[1].split("%")[0])
                mods['hp_percent'] -= value
                print(f"DEBUG: Reduced {value}% HP")

        # Process Mutation Rate - Fixed the value handling
        if "Mutation Rate" in effect_text:
            mutation_value = 0
            if "+%" in effect_text:
                mutation_value = int(effect_text.split("+")[1].split("%")[0])
            elif "-%" in effect_text:
                mutation_value = -int(effect_text.split("-")[1].split("%")[0])
            mods['mutation_rate'] += mutation_value
            print(f"DEBUG: Mutation rate modified by {mutation_value}%")

        # Process Immunities
        if "Immune to" in effect_text:
            immune_type = effect_text.split("Immune to ")[1].split(" ")[0]
            if immune_type not in mods['immunities']:
                mods['immunities'].append(immune_type)
            print(f"DEBUG: Added immunity to {immune_type}")

        # Process Resistances
        if "reduced" in effect_text and "damage" in effect_text:
            resist_value = int(effect_text.split("%")[0])
            damage_type = effect_text.split("reduced ")[1].split(" ")[0]
            mods['resistances'][damage_type] = mods['resistances'].get(damage_type, 0) + resist_value
            print(f"DEBUG: Added {resist_value}% resistance to {damage_type}")

        # Process Resilience
        if "Resilience" in effect_text:
            resil_value = 0
            if "+%" in effect_text:
                resil_value = int(effect_text.split("+")[1].split("%")[0])
            elif "-%" in effect_text:
                resil_value = -int(effect_text.split("-")[1].split("%")[0])
            mods['resistances']['resilience'] = mods['resistances'].get('resilience', 0) + resil_value
            print(f"DEBUG: Resilience modified by {resil_value}%")

    return mods


def calculate_hp(traits):
    """Calculate final HP from base HP and trait modifiers"""
    base_hp = 100
    hp_modifier = 0

    print("\nDEBUG: Calculating HP from traits")

    for trait in traits:
        print(f"DEBUG: Processing HP mods for {trait['name']}")
        for effect in trait.get('effects', []):
            effect_text = effect.get('text', '')

            if "% HP" in effect_text:
                if "+%" in effect_text:
                    value = int(effect_text.split("+")[1].split("%")[0])
                    hp_modifier += value
                    print(f"DEBUG: Added +{value}% HP")
                elif "-%" in effect_text:
                    value = int(effect_text.split("-")[1].split("%")[0])
                    hp_modifier -= value
                    print(f"DEBUG: Subtracted {value}% HP")

    final_hp = base_hp * (1 + (hp_modifier / 100))
    print(f"DEBUG: Final HP calculation: {base_hp} * (1 + {hp_modifier}/100) = {final_hp}")

    return final_hp


def parse_hp_modifier(effect_text: str) -> float:
    """Extract HP modifier from effect text"""
    if "+%" in effect_text:
        return float(effect_text.split("+")[1].split("%")[0])
    elif "-%" in effect_text:
        return -float(effect_text.split("-")[1].split("%")[0])
    return 0.0


def parse_mutation_rate(effect_text: str) -> float:
    """Extract mutation rate from effect text"""
    if "+%" in effect_text:
        return float(effect_text.split("+")[1].split("%")[0])
    elif "-%" in effect_text:
        return -float(effect_text.split("-")[1].split("%")[0])
    return 0.0


def parse_resistance(effect_text: str) -> tuple[str, float]:
    """Extract resistance type and value"""
    value = float(effect_text.split("%")[0])
    damage_type = effect_text.split("reduced ")[1].split(" ")[0].lower()
    return damage_type, value


def parse_immunity(effect_text: str) -> str:
    """Extract immunity type"""
    return effect_text.split("Immune to ")[1].split(" ")[0].lower()


def create_base_stats() -> dict:
    """Create initial stats dictionary"""
    return {
        'base_hp': 100,
        'current_hp': 100,
        'max_hp': 100,
        'mutation_rate': 0,
        'resistances': {},
        'immunities': []
    }


def apply_hp_modifier(stats: dict, hp_multiplier: float) -> None:
    """Apply HP modifier to stats"""
    if hp_multiplier != 0:
        stats['max_hp'] = stats['base_hp'] * (1 + (hp_multiplier / 100))
        stats['current_hp'] = stats['max_hp']
        print(f"DEBUG: Final HP: {stats['max_hp']} ({hp_multiplier}% increase)")


def apply_trait_effects(traits: list) -> dict:
    """Apply effects from all traits to create initial stats"""
    stats = create_base_stats()
    hp_multiplier = 0

    logger.debug("Processing trait effects...")

    for trait in traits:
        logger.debug(f"Processing trait: {trait['name']}")

        for effect in trait.get('effects', []):
            effect_text = effect.get('text', '')

            if "% HP" in effect_text:
                mod = parse_hp_modifier(effect_text)
                hp_multiplier += mod
                logger.debug(f"HP modifier: {mod}% (total: {hp_multiplier}%)")

            elif "Mutation Rate" in effect_text:
                mod = parse_mutation_rate(effect_text)
                stats['mutation_rate'] += mod
                logger.debug(f"Mutation rate: {mod}%")

            elif "Immune to" in effect_text:
                immune_type = parse_immunity(effect_text)
                if immune_type not in stats['immunities']:
                    stats['immunities'].append(immune_type)
                    logger.debug(f"Added immunity: {immune_type}")

    apply_hp_modifier(stats, hp_multiplier)
    logger.debug(f"Final stats: {stats}")
    return stats


def merge_traits(trait1, trait2):
    if trait1["tier"] != trait2["tier"]:
        return None
    if set(trait1["effects"]) != set(trait2["effects"]):
        return None

    new_effect = generate_random_effect(exclude=trait1["effects"])
    return {
        "name": trait1["name"] + "+" + trait2["name"],
        "tier": trait1["tier"],
        "effects": trait1["effects"] + [new_effect],
        "origin": [trait1, trait2],
    }


def generate_random_effect(exclude=None):
    effect_pool = [
        "5% chance to mutate twice",
        "+2% disaster resistance",
        "+3% HP",
        "+1 RP every 30s",
        "+1% mutation rate",
        "10% reduced fire damage",
        "Collapse restores 10 HP once"
    ]
    if exclude:
        effect_pool = [e for e in effect_pool if e not in exclude]
    return random.choice(effect_pool)


def process_trait_effects(stats: Dict, trait: Dict) -> Dict:
    """Process and apply trait effects to stats"""
    hp_multiplier = 1.0

    for effect in trait['effects']:
        effect_text = effect['text'].lower()

        # HP modifications
        if 'hp' in effect_text:
            if match := re.search(r'([+-]\d+)%\s*hp', effect_text):
                mod = float(match.group(1))
                hp_multiplier *= (1 + mod / 100)
                logger.debug(f"HP modifier from {trait['name']}: {mod}%")

        # Entropy reduction
        if 'entropy' in effect_text and 'reduction' in effect_text:
            if match := re.search(r'(\d+)%\s*entropy.*reduction', effect_text):
                value = float(match.group(1))
                current = stats.get('entropy_reduction', 0)
                stats['entropy_reduction'] = min(100, current + value)
                logger.debug(f"Added {value}% entropy reduction from {trait['name']}")

        # Fire resistance (chance to resist)
        if 'chance to resist fire' in effect_text:
            if match := re.search(r'(\d+)%\s*chance', effect_text):
                value = float(match.group(1))
                current = stats.get('fire_resistance', 0)
                stats['resistances']['fire'] = min(100, current + value)

        # Direct damage reduction
        if 'reduced' in effect_text and 'damage' in effect_text:
            if match := re.search(r'(\d+)%\s*reduced\s*(\w+)\s*damage', effect_text):
                value = float(match.group(1))
                dtype = match.group(2)
                current = stats['resistances'].get(dtype, 0)
                stats['resistances'][dtype] = min(100, current + value)

    # Apply HP changes last and round to avoid floating point issues
    stats['max_hp'] = round(stats['max_hp'] * hp_multiplier, 2)
    stats['current_hp'] = stats['max_hp']

    return stats


def calculate_initial_stats(loadout: List[Dict]) -> Dict:
    """Calculate initial stats from trait loadout"""
    stats = {
        'current_hp': 100.0,
        'max_hp': 100.0,
        'mutation_rate': 0.0,
        'resistances': {},
        'immunities': []
    }

    for trait in loadout:
        stats = process_trait_effects(stats, trait)
        logger.debug(f"Processed trait: {trait['name']}")

    # Ensure stats are within bounds
    stats['mutation_rate'] = max(0, stats['mutation_rate'])
    stats['current_hp'] = min(stats['current_hp'], stats['max_hp'])

    return stats
