#!/usr/bin/env python3
# this_file: src/topyaz/system/gpu.py
"""
GPU detection and monitoring for topyaz.

This module provides GPU detection capabilities for different platforms
and vendors (NVIDIA, AMD, Intel, Apple Metal).

"""

import json
import platform
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Optional

from loguru import logger

from topyaz.core.types import GPUInfo, GPUStatus


class GPUDetector(ABC):
    """
    Abstract base class for GPU detection.

    Subclasses implement platform/vendor-specific GPU detection logic.

    Used in:
    - topyaz/system/__init__.py
    """

    @abstractmethod
    def detect(self) -> GPUStatus:
        """
        Detect GPU information.

        Returns:
            GPUStatus object with detected devices

        """
        pass

    def _run_command(self, cmd: list[str], timeout: int = 10) -> tuple[bool, str, str]:
        """
        Run a command and capture output.

        Args:
            cmd: Command to run
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, stdout, stderr)

        """
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)


class NvidiaGPUDetector(GPUDetector):
    """NVIDIA GPU detection using nvidia-smi.

    Used in:
    - topyaz/system/__init__.py
    """

    def detect(self) -> GPUStatus:
        """Detect NVIDIA GPUs using nvidia-smi."""
        if not shutil.which("nvidia-smi"):
            return GPUStatus(available=False, errors=["nvidia-smi not found"])

        # Query GPU information
        cmd = [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,power.draw",
            "--format=csv,noheader,nounits",
        ]

        success, stdout, stderr = self._run_command(cmd)

        if not success:
            return GPUStatus(available=False, errors=[f"nvidia-smi failed: {stderr}"])

        devices = []
        for i, line in enumerate(stdout.strip().split("\n")):
            if not line.strip():
                continue

            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 7:
                try:
                    device = GPUInfo(
                        name=parts[0],
                        type="nvidia",
                        memory_total_mb=int(parts[1]) if parts[1].isdigit() else None,
                        memory_used_mb=int(parts[2]) if parts[2].isdigit() else None,
                        memory_free_mb=int(parts[3]) if parts[3].isdigit() else None,
                        utilization_percent=int(parts[4]) if parts[4].isdigit() else None,
                        temperature_c=int(parts[5]) if parts[5].isdigit() else None,
                        power_draw_w=float(parts[6]) if parts[6].replace(".", "").isdigit() else None,
                        device_id=i,
                    )
                    devices.append(device)
                except (ValueError, IndexError) as e:
                    logger.debug(f"Failed to parse NVIDIA GPU info: {e}")

        return GPUStatus(available=len(devices) > 0, devices=devices)


class AMDGPUDetector(GPUDetector):
    """AMD GPU detection using rocm-smi.

    Used in:
    - topyaz/system/__init__.py
    """

    def detect(self) -> GPUStatus:
        """Detect AMD GPUs using rocm-smi."""
        if not shutil.which("rocm-smi"):
            return GPUStatus(available=False, errors=["rocm-smi not found"])

        # Query basic GPU information
        cmd = ["rocm-smi", "--showid", "--showtemp", "--showuse", "--showmeminfo", "vram"]

        success, stdout, stderr = self._run_command(cmd)

        if not success:
            return GPUStatus(available=False, errors=[f"rocm-smi failed: {stderr}"])

        # Parse AMD GPU output (format is more complex than NVIDIA)
        devices = []
        lines = stdout.strip().split("\n")

        # Simple parsing - AMD output format varies
        gpu_count = 0
        for line in lines:
            if "GPU" in line and any(keyword in line for keyword in ["Device", "Temperature", "Usage"]):
                gpu_count += 1

        # Create basic device entries
        for i in range(gpu_count):
            device = GPUInfo(name=f"AMD GPU {i}", type="amd", device_id=i)
            devices.append(device)

        if devices:
            logger.debug(f"Detected {len(devices)} AMD GPU(s)")

        return GPUStatus(available=len(devices) > 0, devices=devices)


class IntelGPUDetector(GPUDetector):
    """Intel GPU detection.

    Used in:
    - topyaz/system/__init__.py
    """

    def detect(self) -> GPUStatus:
        """Detect Intel GPUs."""
        # Intel GPU detection is platform-specific and less standardized
        if shutil.which("intel_gpu_top"):
            return GPUStatus(available=True, devices=[GPUInfo(name="Intel GPU", type="intel", device_id=0)])

        return GPUStatus(available=False, errors=["Intel GPU tools not found"])


class MetalGPUDetector(GPUDetector):
    """macOS Metal GPU detection.

    Used in:
    - topyaz/system/__init__.py
    """

    def detect(self) -> GPUStatus:
        """Detect Metal GPUs on macOS using system_profiler."""
        if platform.system() != "Darwin":
            return GPUStatus(available=False, errors=["Metal GPU detection only available on macOS"])

        # Use system_profiler to get GPU info
        cmd = ["system_profiler", "SPDisplaysDataType", "-json"]

        success, stdout, stderr = self._run_command(cmd, timeout=15)

        if not success:
            return GPUStatus(available=False, errors=[f"system_profiler failed: {stderr}"])

        try:
            data = json.loads(stdout)
            devices = []

            displays_data = data.get("SPDisplaysDataType", [])

            for i, display in enumerate(displays_data):
                # Look for GPU information
                gpu_name = None
                vram = None

                # Different keys for different macOS versions
                if "sppci_model" in display:
                    gpu_name = display["sppci_model"]
                elif "spdisplays_chipset" in display:
                    gpu_name = display["spdisplays_chipset"]
                elif "_name" in display:
                    gpu_name = display["_name"]

                if "spdisplays_vram" in display:
                    vram = display["spdisplays_vram"]
                elif "spdisplays_gmem" in display:
                    vram = display["spdisplays_gmem"]

                if gpu_name:
                    device = GPUInfo(name=gpu_name, type="metal", vram=vram, device_id=i)

                    # Parse VRAM if possible
                    if vram and isinstance(vram, str):
                        # Extract memory size from strings like "8 GB" or "8192 MB"
                        import re

                        match = re.search(r"(\d+)\s*(GB|MB)", vram, re.IGNORECASE)
                        if match:
                            size = int(match.group(1))
                            unit = match.group(2).upper()
                            if unit == "GB":
                                device.memory_total_mb = size * 1024
                            else:  # MB
                                device.memory_total_mb = size

                    devices.append(device)

            # On Apple Silicon, GPU is integrated
            if not devices and platform.processor() == "arm":
                # Check for Apple Silicon
                devices.append(GPUInfo(name="Apple Silicon GPU", type="metal", device_id=0))

            return GPUStatus(available=len(devices) > 0, devices=devices)

        except (json.JSONDecodeError, KeyError) as e:
            return GPUStatus(available=False, errors=[f"Failed to parse system_profiler output: {e}"])


class GPUManager:
    """
    Manages GPU detection across different platforms and vendors.

    Automatically selects the appropriate detector based on the platform
    and available tools.

    Used in:
    - topyaz/cli.py
    - topyaz/system/__init__.py
    """

    def __init__(self):
        """Initialize GPU manager."""
        self._detector = self._get_detector()
        self._cached_status: GPUStatus | None = None

    def _get_detector(self) -> GPUDetector:
        """
        Get appropriate GPU detector for the current platform.

        Returns:
            GPUDetector instance

        """
        system = platform.system()

        if system == "Darwin":
            # macOS - use Metal detector
            return MetalGPUDetector()

        # For other platforms, try in order of preference
        if shutil.which("nvidia-smi"):
            return NvidiaGPUDetector()

        if shutil.which("rocm-smi"):
            return AMDGPUDetector()

        if shutil.which("intel_gpu_top"):
            return IntelGPUDetector()

        # Fallback - return a dummy detector
        logger.warning("No GPU detection tools found")

        class DummyDetector(GPUDetector):
            """ """

            def detect(self) -> GPUStatus:
                """ """
                return GPUStatus(available=False, errors=["No GPU detection tools available"])

        return DummyDetector()

    def get_status(self, use_cache: bool = True) -> GPUStatus:
        """
        Get current GPU status.

        Args:
            use_cache: Use cached status if available

        Returns:
            GPUStatus object

        Used in:
        - topyaz/cli.py
        """
        if use_cache and self._cached_status is not None:
            return self._cached_status

        logger.debug("Detecting GPU devices...")
        self._cached_status = self._detector.detect()

        if self._cached_status.available:
            logger.info(f"Detected {self._cached_status.count} GPU device(s)")
            for device in self._cached_status.devices:
                logger.debug(f"  - {device.name} (Type: {device.type})")
        else:
            logger.debug("No GPU devices detected")

        return self._cached_status

    def clear_cache(self) -> None:
        """Clear cached GPU status."""
        self._cached_status = None

    def get_device_by_id(self, device_id: int) -> GPUInfo | None:
        """
        Get GPU device by ID.

        Args:
            device_id: Device ID

        Returns:
            GPUInfo object or None if not found

        """
        status = self.get_status()

        for device in status.devices:
            if device.device_id == device_id:
                return device

        return None

    def get_best_device(self) -> GPUInfo | None:
        """
        Get the best available GPU device.

        Selection criteria:
        1. Most available memory
        2. Lowest utilization
        3. First device as fallback

        Returns:
            Best GPUInfo object or None if no devices

        """
        status = self.get_status()

        if not status.devices:
            return None

        # Sort by available memory (descending) and utilization (ascending)
        def score_device(device: GPUInfo) -> tuple:
            mem_free = device.memory_free_mb or 0
            utilization = device.utilization_percent or 100
            return (-mem_free, utilization)

        devices_with_info = [
            d for d in status.devices if d.memory_free_mb is not None or d.utilization_percent is not None
        ]

        if devices_with_info:
            return min(devices_with_info, key=score_device)

        # Fallback to first device
        return status.devices[0]
