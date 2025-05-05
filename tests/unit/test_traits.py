"""
Tests for the trait system
"""
import pytest
from simulacra.core.types import TraitData, GameEffect, EffectType
from simulacra.core.traits import TraitSystem
from simulacra.core.player import Player


def test_trait_system_creation():
    """Test creating a trait system"""
    system = TraitSystem()
    assert system.traits == {}


def test_add_trait():
    """Test adding a trait"""
    system = TraitSystem()

    trait_data: TraitData = {
        'id': 'tough',
        'name': 'Tough',
        'tier': 1,
        'effects': [
            {'type': 'hp', 'value': 10.0, 'text': 'Increases health', 'duration': None}
        ]
    }

    system.add_trait('tough', trait_data)
    assert 'tough' in system.traits
    assert system.traits['tough'] == trait_data


def test_get_trait():
    """Test getting a trait"""
    system = TraitSystem()

    trait_data: TraitData = {
        'id': 'quick',
        'name': 'Quick',
        'tier': 1,
        'effects': [
            {'type': 'hp', 'value': 5.0, 'text': 'Increases speed', 'duration': None}
        ]
    }

    system.add_trait('quick', trait_data)
    retrieved = system.get_trait('quick')
    assert retrieved == trait_data

    # Test getting non-existent trait
    assert system.get_trait('nonexistent') is None


def test_apply_trait_effects():
    """Test applying trait effects to a target"""
    system = TraitSystem()
    player = Player(id='p1', name='Test Player')

    trait_data: TraitData = {
        'id': 'tough',
        'name': 'Tough',
        'tier': 1,
        'effects': [
            {'type': 'hp', 'value': 10.0, 'text': 'Increases health', 'duration': None}
        ]
    }

    system.add_trait('tough', trait_data)
    initial_hp = player.health

    # Apply trait effects
    system.apply_trait_effects('tough', player)
    assert player.health == initial_hp + 10.0


def test_apply_multiple_effects():
    """Test applying multiple effects from a trait"""
    system = TraitSystem()
    player = Player(id='p1', name='Test Player')

    trait_data: TraitData = {
        'id': 'resistant',
        'name': 'Resistant',
        'tier': 2,
        'effects': [
            {'type': 'hp', 'value': 5.0, 'text': 'Minor health boost', 'duration': None},
            {'type': 'resistance', 'value': 10.0, 'text': 'Fire resistance', 'duration': None}
        ]
    }

    system.add_trait('resistant', trait_data)
    initial_hp = player.health

    # Apply trait effects
    system.apply_trait_effects('resistant', player)
    assert player.health == initial_hp + 5.0
    assert player.resistances.get('fire') == 10.0


def test_apply_immunity_effect():
    """Test applying immunity effects"""
    system = TraitSystem()
    player = Player(id='p1', name='Test Player')

    trait_data: TraitData = {
        'id': 'fire_immune',
        'name': 'Fire Immunity',
        'tier': 3,
        'effects': [
            {'type': 'immunity', 'value': 'fire', 'text': 'Immune to fire damage', 'duration': None}
        ]
    }

    system.add_trait('fire_immune', trait_data)
    system.apply_trait_effects('fire_immune', player)
    assert 'fire' in player.immunities


def test_trait_not_found():
    """Test applying non-existent trait"""
    system = TraitSystem()
    player = Player(id='p1', name='Test Player')

    result = system.apply_trait_effects('nonexistent', player)
    assert result is False


def test_stacking_effects():
    """Test stacking multiple effects of same type"""
    system = TraitSystem()
    player = Player(id='p1', name='Test Player')

    trait1: TraitData = {
        'id': 'tough1',
        'name': 'Tough I',
        'tier': 1,
        'effects': [{'type': 'hp', 'value': 10.0, 'text': 'Health boost', 'duration': None}]
    }

    trait2: TraitData = {
        'id': 'tough2',
        'name': 'Tough II',
        'tier': 2,
        'effects': [{'type': 'hp', 'value': 15.0, 'text': 'Greater health boost', 'duration': None}]
    }

    initial_hp = player.health
    system.add_trait('tough1', trait1)
    system.add_trait('tough2', trait2)

    system.apply_trait_effects('tough1', player)
    system.apply_trait_effects('tough2', player)

    assert player.health == initial_hp + 25.0


def test_temporary_effect():
    """Test temporary effects that expire after duration"""
    system = TraitSystem()
    player = Player(id='p1', name='Test Player')

    trait_data: TraitData = {
        'id': 'sprint',
        'name': 'Sprint',
        'tier': 1,
        'effects': [{
            'type': EffectType.SPEED.value,
            'value': 2.0,
            'text': 'Temporary speed boost',
            'duration': 3,
            'remaining': 3
        }],
        'requirements': []
    }

    system.add_trait('sprint', trait_data)
    system.apply_trait_effects('sprint', player)
    assert player.speed == 2.0

    # Simulate turns passing
    for _ in range(3):
        system.update_effects(player)

    assert player.speed == 1.0


def test_trait_requirements():
    """Test trait requirements checking"""
    system = TraitSystem()
    player = Player(id='p1', name='Test Player')

    # Base trait
    trait1: TraitData = {
        'id': 'tough1',
        'name': 'Tough I',
        'tier': 1,
        'effects': [{
            'type': EffectType.HP.value,
            'value': 10.0,
            'text': 'Health boost',
            'duration': None,
            'remaining': None
        }],
        'requirements': []
    }

    # Advanced trait requiring Tough I
    trait2: TraitData = {
        'id': 'tough2',
        'name': 'Tough II',
        'tier': 2,
        'effects': [{
            'type': EffectType.HP.value,
            'value': 20.0,
            'text': 'Greater health boost',
            'duration': None,
            'remaining': None
        }],
        'requirements': [{
            'trait_id': 'tough1',
            'level': 1,
            'stat': None,
            'value': None
        }]
    }

    system.add_trait('tough1', trait1)
    system.add_trait('tough2', trait2)

    # Should fail without requirements
    assert not system.can_apply_trait('tough2', player)

    # Apply base trait first
    system.apply_trait_effects('tough1', player)

    # Now should be able to apply advanced trait
    assert system.can_apply_trait('tough2', player)
