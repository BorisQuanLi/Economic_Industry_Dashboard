import pytest
from repositories.base import DataRepository

class TestDataRepository:
    def test_cannot_instantiate_abstract_base(self):
        """Test that DataRepository cannot be instantiated directly"""
        with pytest.raises(TypeError):
            DataRepository()
            
    def test_concrete_implementation_must_implement_all_methods(self):
        """Test that concrete implementations must implement all abstract methods"""
        class IncompleteRepository(DataRepository):
            pass
            
        with pytest.raises(TypeError):
            IncompleteRepository()
