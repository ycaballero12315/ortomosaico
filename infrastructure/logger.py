import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class LoggerFactory:

    @staticmethod
    def create(
        name: str = "orthomosaic",
        log_dir: Optional[str] = None,
        level: int = logging.INFO,
        console_output: bool = True
    ) -> logging.Logger:
        
        if log_dir is None:
            log_dir = Path.cwd() / "logs"
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{name}_{timestamp}.log"
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if logger.handlers:
            logger.handlers.clear()
        
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler de consola, ojo solo en desarrollo
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        logger.info(f"Logger iniciado - archivo: {log_file}")
        
        return logger
    
    @staticmethod
    def create_simple(name: str = "orthomosaic") -> logging.Logger:
      
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if logger.handlers:
            logger.handlers.clear()
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter('%(levelname)s: %(message)s')
        )
        logger.addHandler(handler)
        
        return logger