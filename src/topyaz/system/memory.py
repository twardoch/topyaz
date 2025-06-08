#!/usr/bin/env python3
# this_file: src/topyaz/system/memory.py
"""
Memory management and optimization for topyaz.

This module provides memory constraint checking and batch size optimization
for different Topaz products based on available system resources.

"""

from typing import Optional

import psutil
from loguru import logger

from topyaz.core.types import MemoryConstraints, Product


class MemoryManager:
    """
    Manages memory constraints and optimization.

    Provides methods to:
    - Check current memory availability
    - Suggest optimal batch sizes
    - Monitor memory usage during operations
    - Provide memory-based recommendations

    Used in:
    - topyaz/cli.py
    - topyaz/system/__init__.py
    """

    # Memory requirements per operation type (in MB per item)
    MEMORY_PER_ITEM = {
        Product.VIDEO_AI: 4096,  # ~4GB per video
        Product.GIGAPIXEL: 512,  # ~512MB per image
        Product.PHOTO_AI: 256,  # ~256MB per image
    }

    # Minimum free memory to maintain (in MB)
    MIN_FREE_MEMORY_MB = 2048  # 2GB

    def __init__(self):
        """Initialize memory manager."""
        self._initial_memory = None
        self._peak_usage = 0

    def check_constraints(self, operation_type: str | Product = "processing") -> MemoryConstraints:
        """
        Check current memory constraints and provide recommendations.

        Args:
            operation_type: Type of operation or Product enum

        Returns:
            MemoryConstraints object with current status and recommendations

        """
        memory = psutil.virtual_memory()

        constraints = MemoryConstraints(
            available_gb=memory.available / (1024**3),
            total_gb=memory.total / (1024**3),
            percent_used=memory.percent,
            recommendations=[],
        )

        # Convert string operation type to Product if possible
        product = None
        if isinstance(operation_type, Product):
            product = operation_type
        else:
            # Try to map string to product
            op_lower = operation_type.lower()
            if "video" in op_lower:
                product = Product.VIDEO_AI
            elif "gigapixel" in op_lower:
                product = Product.GIGAPIXEL
            elif "photo" in op_lower:
                product = Product.PHOTO_AI

        # General memory constraint checks
        if memory.percent > 90:
            constraints.recommendations.append("Critical: Memory usage above 90% - close other applications")
        elif memory.percent > 85:
            constraints.recommendations.append("High memory usage detected - consider reducing batch size")

        if constraints.available_gb < 4:
            constraints.recommendations.append("Low available memory - process files in smaller batches")

        # Product-specific recommendations
        if product == Product.VIDEO_AI:
            if constraints.available_gb < 16:
                constraints.recommendations.append("Video AI: Less than 16GB available - process one video at a time")
            if constraints.total_gb < 32:
                constraints.recommendations.append("Video AI: Consider upgrading to 32GB+ RAM for better performance")

        elif product == Product.GIGAPIXEL:
            if constraints.available_gb < 4:
                constraints.recommendations.append("Gigapixel: Low memory may cause processing failures")
            if constraints.available_gb < 8:
                constraints.recommendations.append("Gigapixel: Reduce batch size to 5-10 images")

        elif product == Product.PHOTO_AI:
            if constraints.available_gb < 2:
                constraints.recommendations.append("Photo AI: Very low memory - process in small batches")

        logger.debug(
            f"Memory check for {operation_type}: "
            f"{constraints.available_gb:.1f}GB available, "
            f"{constraints.percent_used:.1f}% used"
        )

        return constraints

    def get_optimal_batch_size(
        self,
        file_count: int,
        operation_type: str | Product = "processing",
        file_size_mb: float | None = None,
        safety_factor: float = 0.8,
    ) -> int:
        """
        Calculate optimal batch size based on available memory.

        Args:
            file_count: Total number of files to process
            operation_type: Type of operation or Product enum
            file_size_mb: Average file size in MB (for better estimation)
            safety_factor: Safety factor (0-1) to prevent OOM

        Returns:
            Optimal batch size

        Used in:
        - topyaz/cli.py
        """
        if file_count == 0:
            return 0

        memory = psutil.virtual_memory()
        available_mb = memory.available / (1024**2)

        # Reserve minimum free memory
        usable_memory_mb = max(0, (available_mb - self.MIN_FREE_MEMORY_MB) * safety_factor)

        # Determine memory per item
        if isinstance(operation_type, Product):
            memory_per_item = self.MEMORY_PER_ITEM.get(
                operation_type,
                256,  # Default
            )
        else:
            # String-based operation type
            op_lower = operation_type.lower()
            if "video" in op_lower:
                memory_per_item = self.MEMORY_PER_ITEM[Product.VIDEO_AI]
            elif "gigapixel" in op_lower:
                memory_per_item = self.MEMORY_PER_ITEM[Product.GIGAPIXEL]
            elif "photo" in op_lower:
                memory_per_item = self.MEMORY_PER_ITEM[Product.PHOTO_AI]
            else:
                memory_per_item = 256  # Default

        # Adjust based on file size if provided
        if file_size_mb:
            # Use file size as a factor
            memory_per_item = max(memory_per_item, file_size_mb * 2)

        # Calculate batch size
        if usable_memory_mb <= 0:
            batch_size = 1  # Minimum batch size
        else:
            batch_size = int(usable_memory_mb / memory_per_item)

        # Apply product-specific limits
        if isinstance(operation_type, Product):
            if operation_type == Product.VIDEO_AI:
                # Video AI typically processes one at a time
                batch_size = min(batch_size, 4)
            elif operation_type == Product.GIGAPIXEL:
                # Gigapixel can handle more in parallel
                batch_size = min(batch_size, 50)
            elif operation_type == Product.PHOTO_AI:
                # Photo AI has a hard limit around 450
                batch_size = min(batch_size, 400)

        # Never exceed file count
        batch_size = max(1, min(batch_size, file_count))

        logger.debug(
            f"Optimal batch size for {operation_type}: {batch_size} "
            f"(from {file_count} files, {usable_memory_mb:.0f}MB usable)"
        )

        return batch_size

    def start_monitoring(self) -> None:
        """Start memory monitoring for an operation."""
        self._initial_memory = psutil.virtual_memory()
        self._peak_usage = self._initial_memory.used
        logger.debug(f"Memory monitoring started: {self._initial_memory.percent:.1f}% used")

    def update_monitoring(self) -> dict[str, float]:
        """
        Update memory monitoring and return current stats.

        Returns:
            Dictionary with memory statistics

        """
        if self._initial_memory is None:
            self.start_monitoring()

        current_memory = psutil.virtual_memory()
        self._peak_usage = max(self._peak_usage, current_memory.used)

        return {
            "current_used_gb": current_memory.used / (1024**3),
            "current_percent": current_memory.percent,
            "peak_used_gb": self._peak_usage / (1024**3),
            "delta_gb": (current_memory.used - self._initial_memory.used) / (1024**3),
        }

    def stop_monitoring(self) -> dict[str, float]:
        """
        Stop memory monitoring and return final stats.

        Returns:
            Dictionary with final memory statistics

        """
        stats = self.update_monitoring()

        logger.debug(
            f"Memory monitoring stopped: Peak usage: {stats['peak_used_gb']:.1f}GB, Delta: {stats['delta_gb']:+.1f}GB"
        )

        self._initial_memory = None
        self._peak_usage = 0

        return stats

    def suggest_recovery_action(self, error_message: str, operation_type: str | Product = "processing") -> list[str]:
        """
        Suggest recovery actions based on error message.

        Args:
            error_message: Error message from failed operation
            operation_type: Type of operation that failed

        Returns:
            List of suggested recovery actions

        """
        suggestions = []
        error_lower = error_message.lower()

        # Check for memory-related keywords
        memory_keywords = ["memory", "ram", "allocation", "out of memory", "oom", "insufficient", "failed to allocate"]

        if any(keyword in error_lower for keyword in memory_keywords):
            current_memory = self.check_constraints(operation_type)

            suggestions.append("Memory issue detected. Try:")
            suggestions.append(f"- Current memory usage: {current_memory.percent_used:.1f}%")
            suggestions.append(f"- Available: {current_memory.available_gb:.1f}GB")

            # Add specific suggestions
            suggestions.extend(current_memory.recommendations)

            # General suggestions
            suggestions.append("- Close other applications")
            suggestions.append("- Reduce batch size to 1")
            suggestions.append("- Restart the application")

            # Product-specific suggestions
            if isinstance(operation_type, Product):
                if operation_type == Product.VIDEO_AI:
                    suggestions.append("- Lower output resolution or quality")
                    suggestions.append("- Process shorter segments")
                elif operation_type == Product.GIGAPIXEL:
                    suggestions.append("- Process smaller images first")
                    suggestions.append("- Reduce scale factor")
                elif operation_type == Product.PHOTO_AI:
                    suggestions.append("- Disable some enhancement features")
                    suggestions.append("- Process JPEG instead of RAW")

        return suggestions

    def can_process_batch(
        self, batch_size: int, operation_type: str | Product = "processing", required_memory_mb: float | None = None
    ) -> tuple[bool, str]:
        """
        Check if system can process a batch of given size.

        Args:
            batch_size: Number of items in batch
            operation_type: Type of operation
            required_memory_mb: Override memory requirement per item

        Returns:
            Tuple of (can_process, reason_if_not)

        """
        memory = psutil.virtual_memory()
        available_mb = memory.available / (1024**2)

        # Determine memory requirement
        if required_memory_mb is None:
            if isinstance(operation_type, Product):
                required_memory_mb = self.MEMORY_PER_ITEM.get(operation_type, 256)
            else:
                required_memory_mb = 256  # Default

        total_required = batch_size * required_memory_mb

        # Check if we have enough memory
        if total_required > available_mb - self.MIN_FREE_MEMORY_MB:
            return False, (f"Insufficient memory: {total_required:.0f}MB required, {available_mb:.0f}MB available")

        # Check if memory usage is already high
        if memory.percent > 90:
            return False, f"Memory usage too high: {memory.percent:.1f}%"

        return True, "OK"
