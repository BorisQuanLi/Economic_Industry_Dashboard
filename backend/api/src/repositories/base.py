from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class DataRepository(ABC):
    @abstractmethod
    def get_sectors(self) -> List[str]:
        pass
        
    @abstractmethod
    def get_sector_metrics(self, sector: str) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def store_raw_data(self, data: Dict[str, Any], dataset_name: str) -> bool:
        pass
