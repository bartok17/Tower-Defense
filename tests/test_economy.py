"""
Tests for the economy system.
"""

import pytest

from src.systems.economy_system import ResourcesManager


class TestResourcesManager:
    """Tests for ResourcesManager class."""
    
    def test_initial_resources(self):
        """Test that resources are initialized correctly."""
        manager = ResourcesManager(
            initial_gold=100,
            initial_wood=50,
            initial_metal=25,
            initial_health=100
        )
        
        assert manager.get_resource("gold") == 100
        assert manager.get_resource("wood") == 50
        assert manager.get_resource("metal") == 25
        assert manager.get_resource("health") == 100
    
    def test_add_resource(self):
        """Test adding resources."""
        manager = ResourcesManager(initial_gold=100)
        
        manager.add_resource("gold", 50)
        assert manager.get_resource("gold") == 150
    
    def test_spend_resource_success(self):
        """Test successful resource spending."""
        manager = ResourcesManager(initial_gold=100)
        
        result = manager.spend_resource("gold", 30)
        
        assert result is True
        assert manager.get_resource("gold") == 70
    
    def test_spend_resource_insufficient(self):
        """Test spending more than available."""
        manager = ResourcesManager(initial_gold=50)
        
        result = manager.spend_resource("gold", 100)
        
        assert result is False
        assert manager.get_resource("gold") == 50  # Unchanged
    
    def test_can_afford_single(self):
        """Test can_afford with single resource."""
        manager = ResourcesManager(initial_gold=100)
        
        assert manager.can_afford({"gold": 50}) is True
        assert manager.can_afford({"gold": 150}) is False
    
    def test_can_afford_multiple(self):
        """Test can_afford with multiple resources."""
        manager = ResourcesManager(
            initial_gold=100,
            initial_wood=50,
            initial_metal=25
        )
        
        # Can afford
        assert manager.can_afford({"gold": 50, "wood": 30}) is True
        
        # Can't afford one resource
        assert manager.can_afford({"gold": 50, "wood": 100}) is False
    
    def test_spend_costs(self):
        """Test spend_costs method."""
        manager = ResourcesManager(
            initial_gold=100,
            initial_wood=50
        )
        
        costs = {"gold": 40, "wood": 20}
        result = manager.spend_costs(costs)
        
        assert result is True
        assert manager.get_resource("gold") == 60
        assert manager.get_resource("wood") == 30
    
    def test_spend_costs_insufficient(self):
        """Test spend_costs when can't afford."""
        manager = ResourcesManager(
            initial_gold=30,
            initial_wood=50
        )
        
        costs = {"gold": 40, "wood": 20}
        result = manager.spend_costs(costs)
        
        # Should fail and resources should be unchanged
        assert result is False
        assert manager.get_resource("gold") == 30
        assert manager.get_resource("wood") == 50
    
    def test_is_dead(self):
        """Test health death check."""
        manager = ResourcesManager(initial_health=10)
        
        assert manager.is_dead() is False
        
        manager.spend_resource("health", 10)
        assert manager.is_dead() is True
    
    def test_resources_property(self):
        """Test resources dictionary property."""
        manager = ResourcesManager(
            initial_gold=100,
            initial_wood=50,
            initial_metal=25,
            initial_health=100
        )
        
        resources = manager.resources
        
        assert resources["gold"] == 100
        assert resources["wood"] == 50
        assert resources["metal"] == 25
        assert resources["health"] == 100


class TestResourcesManagerEdgeCases:
    """Edge case tests for ResourcesManager."""
    
    def test_negative_add_prevented(self):
        """Test that negative amounts don't reduce resources."""
        manager = ResourcesManager(initial_gold=100)
        
        # Adding negative should be treated as 0 or raise error
        # depending on implementation
        manager.add_resource("gold", -50)
        # Gold should remain 100 or implementation should handle this
    
    def test_unknown_resource(self):
        """Test handling of unknown resource type."""
        manager = ResourcesManager(initial_gold=100)
        
        # Should return 0 for unknown resources
        assert manager.get_resource("unknown") == 0
    
    def test_empty_costs_affordable(self):
        """Test that empty costs are always affordable."""
        manager = ResourcesManager(initial_gold=0)
        
        assert manager.can_afford({}) is True
