#!/usr/bin/env python3
# this_file: src/topyaz/topyaz.py
"""
topyaz: Unified Python CLI wrapper for Topaz Labs products.

This module provides the main topyazWrapper class that serves as a unified interface
for Topaz Video AI, Gigapixel AI, and Photo AI products with support for local and
remote execution via SSH.

Created by Adam Twardoch

"""

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import psutil
import yaml
from loguru import logger
from tqdm import tqdm

try:
    from topyaz.__version__ import __version__
except ImportError:
    __version__ = "0.1.0-dev"


class TopazError(Exception):
    """Base exception for topyaz errors.

    Used in:
    - topyaz/__init__.py
    """

    pass


class AuthenticationError(TopazError):
    """Authentication-related errors.

    Used in:
    - topyaz/__init__.py
    """

    pass


class EnvironmentError(TopazError):
    """Environment validation errors.

    Used in:
    - topyaz/__init__.py
    """

    pass


class ProcessingError(TopazError):
    """Processing-related errors.

    Used in:
    - topyaz/__init__.py
    """

    pass


class topyazWrapper:
    """
    Unified wrapper for Topaz Labs products (Video AI, Gigapixel AI, Photo AI).

    Provides a consistent interface across all three products with support for:
    - Local and remote execution via SSH
    - Comprehensive error handling and validation
    - Progress monitoring and logging
    - Configuration management

    Used in:
    - topyaz/__init__.py
    - topyaz/__main__.py
    """

    def __init__(
        self,
        remote_host: str | None = None,
        ssh_user: str | None = None,
        ssh_key: str | None = None,
        verbose: bool = True,
        dry_run: bool = False,
        log_level: str = "INFO",
        timeout: int = 3600,
        parallel_jobs: int = 1,
        output_dir: str | None = None,
        preserve_structure: bool = True,
        backup_originals: bool = False,
        config_file: str | None = None,
    ):
        """
        Initialize the topyaz wrapper with unified options.

        Args:
            remote_host: Remote machine hostname/IP for SSH execution
            ssh_user: SSH username for remote execution
            ssh_key: Path to SSH private key file
            verbose: Enable detailed output and progress reporting
            dry_run: Show commands without executing them
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            timeout: Maximum execution time in seconds per operation
            parallel_jobs: Number of concurrent operations (where supported)
            output_dir: Default output directory for processed files
            preserve_structure: Maintain input directory structure in output
            backup_originals: Create backup copies before processing
            config_file: Path to YAML configuration file

        """
        # Store initialization parameters
        self.remote_host = remote_host
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.verbose = verbose
        self.dry_run = dry_run
        self.timeout = timeout
        self.parallel_jobs = parallel_jobs
        self.output_dir = output_dir
        self.preserve_structure = preserve_structure
        self.backup_originals = backup_originals

        # Initialize logging
        self._setup_logging(log_level)

        # Load configuration
        self.config = self._load_config(config_file)

        # Initialize product executables
        self._gigapixel_exe = None
        self._video_ai_ffmpeg = None
        self._photo_ai_exe = None

        # Initialize environment
        self._validate_environment()

        logger.info(f"topyaz v{__version__} initialized")
        if self.dry_run:
            logger.info("DRY RUN MODE: Commands will be shown but not executed")

    def _setup_logging(self, log_level: str) -> None:
        """Configure loguru logging system."""
        logger.remove()  # Remove default handler

        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        # Console handler
        logger.add(
            lambda msg: print(msg, end=""),
            format=log_format,
            level=log_level,
            colorize=True,
        )

        # File handler if verbose mode
        if self.verbose:
            log_file = Path.home() / ".topyaz" / "logs" / "topyaz.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                log_file,
                format=log_format,
                level="DEBUG",
                rotation="10 MB",
                retention="1 week",
            )

    def _load_config(self, config_file: str | None) -> dict[str, Any]:
        """Load configuration from YAML file."""
        config_path = Path(config_file) if config_file else Path.home() / ".topyaz" / "config.yaml"

        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f) or {}
                logger.debug(f"Loaded configuration from {config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

        # Return default configuration
        return {
            "defaults": {
                "output_dir": "~/processed",
                "preserve_structure": True,
                "backup_originals": False,
                "log_level": "INFO",
            },
            "video": {"default_model": "amq-13", "default_codec": "hevc_videotoolbox", "default_quality": 18},
            "gigapixel": {"default_model": "std", "default_format": "preserve", "parallel_read": 4},
            "photo": {"default_format": "jpg", "default_quality": 95},
        }

    def _validate_environment(self) -> None:
        """Validate system environment and requirements."""
        # Check macOS version
        if platform.system() == "Darwin":
            version = platform.mac_ver()[0]
            major, minor = map(int, version.split(".")[:2])
            if major < 11:
                logger.warning("macOS 11+ recommended for full Topaz support")

        # Check available memory
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb < 16:
            logger.warning(f"Low memory detected ({memory_gb:.1f}GB). 16GB+ recommended")

        # Check available disk space
        disk_free_gb = psutil.disk_usage(Path.home()).free / (1024**3)
        if disk_free_gb < 80:
            logger.warning(f"Low disk space ({disk_free_gb:.1f}GB). 80GB+ recommended for Video AI")

    def _check_memory_constraints(self, operation_type: str = "processing") -> dict[str, Any]:
        """Check current memory constraints and suggest optimizations."""
        memory = psutil.virtual_memory()

        constraints = {
            "available_gb": memory.available / (1024**3),
            "total_gb": memory.total / (1024**3),
            "percent_used": memory.percent,
            "recommendations": [],
        }

        # Memory constraint detection
        if memory.percent > 85:
            constraints["recommendations"].append("High memory usage detected - consider reducing batch size")

        if constraints["available_gb"] < 8:
            constraints["recommendations"].append("Low available memory - process files in smaller batches")

        if operation_type == "video" and constraints["available_gb"] < 16:
            constraints["recommendations"].append("Video processing requires 16GB+ RAM for optimal performance")

        if operation_type == "gigapixel" and constraints["available_gb"] < 4:
            constraints["recommendations"].append("Gigapixel processing may fail with less than 4GB available RAM")

        logger.debug(
            f"Memory check: {constraints['available_gb']:.1f}GB available, {constraints['percent_used']:.1f}% used"
        )

        return constraints

    def _get_optimal_batch_size(self, file_count: int, operation_type: str = "processing") -> int:
        """Calculate optimal batch size based on available system resources."""
        memory_constraints = self._check_memory_constraints(operation_type)
        available_gb = memory_constraints["available_gb"]

        # Base batch sizes by operation type and available memory
        if operation_type == "video":
            if available_gb >= 32:
                base_batch = 4
            elif available_gb >= 16:
                base_batch = 2
            else:
                base_batch = 1
        elif operation_type == "gigapixel":
            if available_gb >= 32:
                base_batch = 50
            elif available_gb >= 16:
                base_batch = 25
            elif available_gb >= 8:
                base_batch = 10
            else:
                base_batch = 5
        elif operation_type == "photo":
            # Photo AI has a hard limit of ~450 images per batch
            if available_gb >= 16:
                base_batch = 400
            elif available_gb >= 8:
                base_batch = 200
            else:
                base_batch = 100
        else:
            base_batch = min(10, file_count)

        # Don't exceed available files
        optimal_batch = min(base_batch, file_count)

        logger.debug(f"Optimal batch size for {operation_type}: {optimal_batch} (from {file_count} files)")

        return optimal_batch

    def _handle_processing_error(self, error: Exception, operation_type: str, retry_count: int = 0) -> bool:
        """Handle processing errors with intelligent recovery strategies."""
        max_retries = 3

        if retry_count >= max_retries:
            logger.error(f"Max retries ({max_retries}) exceeded for {operation_type}")
            return False

        error_msg = str(error).lower()

        # Memory-related errors
        if any(keyword in error_msg for keyword in ["memory", "ram", "allocation", "out of memory"]):
            logger.warning(f"Memory error detected in {operation_type} - suggesting batch size reduction")

            # Log memory recovery suggestions
            memory_constraints = self._check_memory_constraints(operation_type)
            for recommendation in memory_constraints["recommendations"]:
                logger.info(f"Recovery suggestion: {recommendation}")

            return True  # Suggest retry with smaller batch

        # GPU-related errors
        if any(keyword in error_msg for keyword in ["gpu", "cuda", "opencl", "metal", "device"]):
            logger.warning(f"GPU error detected in {operation_type} - consider CPU fallback")
            logger.info("Recovery suggestion: Try running with device=-1 to force CPU processing")
            return True

        # Authentication errors
        if any(keyword in error_msg for keyword in ["auth", "login", "token", "license"]):
            logger.error(f"Authentication error in {operation_type} - please login via GUI")
            logger.info("Recovery suggestion: Open the Topaz app and ensure you're logged in")
            return False  # Don't retry auth errors automatically

        # File permission errors
        if any(keyword in error_msg for keyword in ["permission", "access", "denied", "readonly"]):
            logger.error(f"File permission error in {operation_type}")
            logger.info("Recovery suggestion: Check file/directory permissions and disk space")
            return False  # Don't retry permission errors

        # Unknown errors - allow one retry
        if retry_count == 0:
            logger.warning(f"Unknown error in {operation_type}, attempting retry: {error}")
            return True

        logger.error(f"Unrecoverable error in {operation_type}: {error}")
        return False

    def _get_gpu_info(self) -> dict[str, Any]:
        """Get GPU information and utilization statistics."""
        gpu_info = {"available": False, "devices": [], "utilization": {}, "memory": {}, "errors": []}

        try:
            # Try NVIDIA GPUs first
            if shutil.which("nvidia-smi"):
                gpu_info.update(self._get_nvidia_gpu_info())

            # Try AMD GPUs
            elif shutil.which("rocm-smi"):
                gpu_info.update(self._get_amd_gpu_info())

            # Try Intel GPUs
            elif shutil.which("intel_gpu_top"):
                gpu_info.update(self._get_intel_gpu_info())

            # macOS Metal performance (Apple Silicon)
            elif platform.system() == "Darwin":
                gpu_info.update(self._get_metal_gpu_info())

        except Exception as e:
            gpu_info["errors"].append(f"GPU detection error: {e}")
            logger.debug(f"GPU detection failed: {e}")

        return gpu_info

    def _get_nvidia_gpu_info(self) -> dict[str, Any]:
        """Get NVIDIA GPU information using nvidia-smi."""
        import subprocess

        try:
            # Query GPU information
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw",
                "--format=csv,noheader,nounits",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)

            if result.returncode != 0:
                return {"available": False, "errors": [f"nvidia-smi failed: {result.stderr}"]}

            devices = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 6:
                        devices.append(
                            {
                                "name": parts[0],
                                "memory_total_mb": int(parts[1]) if parts[1].isdigit() else 0,
                                "memory_used_mb": int(parts[2]) if parts[2].isdigit() else 0,
                                "utilization_percent": int(parts[3]) if parts[3].isdigit() else 0,
                                "temperature_c": int(parts[4]) if parts[4].isdigit() else 0,
                                "power_draw_w": float(parts[5]) if parts[5].replace(".", "").isdigit() else 0.0,
                            }
                        )

            return {"available": True, "type": "nvidia", "devices": devices, "count": len(devices)}

        except Exception as e:
            return {"available": False, "errors": [f"NVIDIA GPU detection error: {e}"]}

    def _get_amd_gpu_info(self) -> dict[str, Any]:
        """Get AMD GPU information using rocm-smi."""
        import subprocess

        try:
            # Query basic GPU information
            result = subprocess.run(
                ["rocm-smi", "--showid", "--showtemp", "--showuse"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                return {"available": False, "errors": [f"rocm-smi failed: {result.stderr}"]}

            # Basic parsing - AMD output format is more complex
            devices = []
            lines = result.stdout.strip().split("\n")

            for line in lines:
                if "GPU" in line and "%" in line:
                    # Simple extraction - would need more sophisticated parsing for production
                    devices.append({"name": "AMD GPU", "type": "amd", "utilization_info": line.strip()})

            return {"available": True, "type": "amd", "devices": devices, "count": len(devices)}

        except Exception as e:
            return {"available": False, "errors": [f"AMD GPU detection error: {e}"]}

    def _get_intel_gpu_info(self) -> dict[str, Any]:
        """Get Intel GPU information."""
        # Intel GPU monitoring is less standardized
        return {
            "available": True,
            "type": "intel",
            "devices": [{"name": "Intel GPU", "note": "Limited monitoring available"}],
            "count": 1,
        }

    def _get_metal_gpu_info(self) -> dict[str, Any]:
        """Get macOS Metal GPU information for Apple Silicon."""
        try:
            # Use system_profiler to get GPU info
            import subprocess

            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType", "-json"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                return {"available": False, "errors": ["system_profiler failed"]}

            import json

            data = json.loads(result.stdout)

            devices = []
            displays = data.get("SPDisplaysDataType", [])

            for display in displays:
                if "sppci_model" in display or "spdisplays_chipset" in display:
                    gpu_name = display.get("sppci_model", display.get("spdisplays_chipset", "Unknown GPU"))

                    # Extract VRAM if available
                    vram = display.get("spdisplays_vram", "Unknown")

                    devices.append({"name": gpu_name, "vram": vram, "type": "metal"})

            return {"available": True, "type": "metal", "devices": devices, "count": len(devices)}

        except Exception as e:
            return {"available": False, "errors": [f"Metal GPU detection error: {e}"]}

    def _monitor_gpu_during_processing(self, duration_seconds: int = 60) -> dict[str, Any]:
        """Monitor GPU utilization during processing for specified duration."""
        import threading
        import time

        monitoring_data = {
            "samples": [],
            "peak_utilization": 0,
            "average_utilization": 0,
            "peak_memory_usage": 0,
            "monitoring_duration": duration_seconds,
        }

        start_time = time.time()
        sample_interval = 2  # seconds

        while time.time() - start_time < duration_seconds:
            gpu_info = self._get_gpu_info()

            if gpu_info["available"] and gpu_info["devices"]:
                sample = {"timestamp": time.time(), "devices": []}

                for device in gpu_info["devices"]:
                    if "utilization_percent" in device:
                        utilization = device["utilization_percent"]
                        monitoring_data["peak_utilization"] = max(monitoring_data["peak_utilization"], utilization)

                        sample["devices"].append(
                            {
                                "name": device["name"],
                                "utilization": utilization,
                                "memory_used": device.get("memory_used_mb", 0),
                            }
                        )

                        memory_used = device.get("memory_used_mb", 0)
                        monitoring_data["peak_memory_usage"] = max(monitoring_data["peak_memory_usage"], memory_used)

                monitoring_data["samples"].append(sample)

            time.sleep(sample_interval)

        # Calculate average utilization
        if monitoring_data["samples"]:
            total_utilization = sum(
                device["utilization"] for sample in monitoring_data["samples"] for device in sample["devices"]
            )
            total_measurements = sum(len(sample["devices"]) for sample in monitoring_data["samples"])

            if total_measurements > 0:
                monitoring_data["average_utilization"] = total_utilization / total_measurements

        return monitoring_data

    def _find_executable(self, product: str) -> str | None:
        """Find executable for specified Topaz product."""
        if platform.system() == "Darwin":  # macOS
            paths = {
                "gigapixel": [
                    "/Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/gigapixel",
                    "/Applications/Topaz Gigapixel AI.app/Contents/MacOS/Topaz Gigapixel AI",
                ],
                "video_ai": ["/Applications/Topaz Video AI.app/Contents/MacOS/ffmpeg"],
                "photo_ai": [
                    "/Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai",
                    "/Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI",
                ],
            }
        elif platform.system() == "Windows":
            paths = {
                "gigapixel": ["C:\\Program Files\\Topaz Labs LLC\\Topaz Gigapixel AI\\bin\\gigapixel.exe"],
                "video_ai": ["C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\ffmpeg.exe"],
                "photo_ai": ["C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI\\tpai.exe"],
            }
        else:
            logger.error(f"Unsupported platform: {platform.system()}")
            return None

        for path in paths.get(product, []):
            if Path(path).exists():
                logger.debug(f"Found {product} executable: {path}")
                return path

        logger.warning(f"Could not find {product} executable")
        return None

    def _execute_command(self, command: list[str], input_data: str | None = None) -> tuple[int, str, str]:
        """Execute a command locally or remotely."""
        if self.dry_run:
            logger.info(f"DRY RUN: {' '.join(command)}")
            return 0, "dry-run-output", ""

        if self.remote_host:
            return self._execute_remote(command, input_data)
        return self._execute_local(command, input_data)

    def _execute_local(self, command: list[str], input_data: str | None = None) -> tuple[int, str, str]:
        """Execute command locally."""
        try:
            logger.debug(f"Executing: {' '.join(command)}")

            result = subprocess.run(
                command,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding="utf-8",
                errors="ignore",
                check=False,
            )

            logger.debug(f"Return code: {result.returncode}")
            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr:
                logger.debug(f"STDERR: {result.stderr}")

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            msg = f"Command timed out after {self.timeout} seconds"
            raise ProcessingError(msg)
        except Exception as e:
            msg = f"Command execution failed: {e}"
            raise ProcessingError(msg)

    def _execute_remote(self, command: list[str], input_data: str | None = None) -> tuple[int, str, str]:
        """Execute command on remote host via SSH."""
        if not self.ssh_user:
            msg = "SSH user required for remote execution"
            raise OSError(msg)

        import io

        import paramiko

        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to remote host
            connect_kwargs = {"hostname": self.remote_host, "username": self.ssh_user, "timeout": 30}

            if self.ssh_key:
                connect_kwargs["key_filename"] = self.ssh_key

            logger.debug(f"Connecting to {self.remote_host} as {self.ssh_user}")
            ssh.connect(**connect_kwargs)

            # Execute command
            command_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in command)
            logger.debug(f"Remote command: {command_str}")

            stdin, stdout, stderr = ssh.exec_command(command_str, timeout=self.timeout)

            if input_data:
                stdin.write(input_data)
                stdin.flush()

            # Get results
            exit_status = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode("utf-8", errors="ignore")
            stderr_data = stderr.read().decode("utf-8", errors="ignore")

            logger.debug(f"Remote exit status: {exit_status}")
            if stdout_data:
                logger.debug(f"Remote STDOUT: {stdout_data}")
            if stderr_data:
                logger.debug(f"Remote STDERR: {stderr_data}")

            ssh.close()
            return exit_status, stdout_data, stderr_data

        except paramiko.AuthenticationException:
            msg = f"SSH authentication failed for {self.ssh_user}@{self.remote_host}"
            raise AuthenticationError(msg)
        except paramiko.SSHException as e:
            msg = f"SSH connection error: {e}"
            raise ProcessingError(msg)
        except Exception as e:
            msg = f"Remote execution failed: {e}"
            raise ProcessingError(msg)

    def _execute_command_with_progress(self, command: list[str], task_name: str) -> tuple[int, str, str]:
        """Execute command with progress monitoring."""
        import subprocess
        import threading
        import time

        try:
            logger.debug(f"Executing with progress: {' '.join(command)}")

            # Start process
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore"
            )

            # Progress bar setup
            progress_bar = tqdm(
                desc=task_name,
                unit=" frames" if "video" in task_name.lower() else " images",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            )

            stdout_data = []
            stderr_data = []

            def read_output(pipe, data_list):
                for line in iter(pipe.readline, ""):
                    data_list.append(line)
                    # Update progress based on output patterns
                    if "Processing" in line or "frame=" in line:
                        progress_bar.update(1)
                pipe.close()

            # Start output reading threads
            stdout_thread = threading.Thread(target=read_output, args=(process.stdout, stdout_data))
            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, stderr_data))

            stdout_thread.start()
            stderr_thread.start()

            # Wait for process with timeout
            try:
                exit_code = process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                progress_bar.close()
                msg = f"Command timed out after {self.timeout} seconds"
                raise ProcessingError(msg)

            # Wait for threads to finish
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)

            progress_bar.close()

            stdout_str = "".join(stdout_data)
            stderr_str = "".join(stderr_data)

            logger.debug(f"Return code: {exit_code}")
            if stdout_str:
                logger.debug(f"STDOUT: {stdout_str}")
            if stderr_str:
                logger.debug(f"STDERR: {stderr_str}")

            return exit_code, stdout_str, stderr_str

        except Exception as e:
            if "progress_bar" in locals():
                progress_bar.close()
            msg = f"Command execution failed: {e}"
            raise ProcessingError(msg)

    def _validate_paths(self, input_path: str, output_path: str | None = None) -> tuple[Path, Path]:
        """Validate and normalize input/output paths."""
        # Expand and resolve input path
        input_path_obj = Path(input_path).expanduser().resolve()

        if not input_path_obj.exists():
            msg = f"Input path does not exist: {input_path}"
            raise ValueError(msg)

        # Determine output path
        if output_path:
            output_path_obj = Path(output_path).expanduser().resolve()
        elif self.output_dir:
            output_path_obj = Path(self.output_dir).expanduser().resolve()
        # Default to input directory with '_processed' suffix
        elif input_path_obj.is_file():
            output_path_obj = input_path_obj.parent / f"{input_path_obj.stem}_processed"
        else:
            output_path_obj = input_path_obj.parent / f"{input_path_obj.name}_processed"

        # Create output directory if it doesn't exist
        output_path_obj.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Input path: {input_path_obj}")
        logger.debug(f"Output path: {output_path_obj}")

        return input_path_obj, output_path_obj

    def _validate_gigapixel_params(
        self,
        model: str,
        scale: int,
        denoise: int | None,
        sharpen: int | None,
        compression: int | None,
        detail: int | None,
        creativity: int | None,
        texture: int | None,
        face_recovery: int | None,
        face_recovery_version: int,
        format: str,
        quality: int,
        bit_depth: int,
        parallel_read: int,
    ) -> None:
        """Validate Gigapixel AI parameters."""
        # Valid models
        valid_models = {
            "std",
            "standard",
            "hf",
            "high fidelity",
            "fidelity",
            "low",
            "lowres",
            "low resolution",
            "low res",
            "art",
            "cg",
            "cgi",
            "lines",
            "compression",
            "very compressed",
            "high compression",
            "vc",
            "text",
            "txt",
            "text refine",
            "recovery",
            "redefine",
        }
        if model not in valid_models:
            msg = f"Invalid model '{model}'. Valid models: {', '.join(sorted(valid_models))}"
            raise ValueError(msg)

        # Scale validation
        if scale < 1 or scale > 6:
            msg = "Scale must be between 1 and 6"
            raise ValueError(msg)

        # Parameter range validations
        for param_name, param_value, min_val, max_val in [
            ("denoise", denoise, 1, 100),
            ("sharpen", sharpen, 1, 100),
            ("compression", compression, 1, 100),
            ("detail", detail, 1, 100),
            ("creativity", creativity, 1, 6),
            ("texture", texture, 1, 6),
            ("face_recovery", face_recovery, 1, 100),
            ("quality", quality, 1, 100),
            ("parallel_read", parallel_read, 1, 10),
        ]:
            if param_value is not None and (param_value < min_val or param_value > max_val):
                msg = f"{param_name} must be between {min_val} and {max_val}"
                raise ValueError(msg)

        # Face recovery version validation
        if face_recovery_version not in [1, 2]:
            msg = "Face recovery version must be 1 or 2"
            raise ValueError(msg)

        # Format validation
        valid_formats = {"preserve", "jpg", "jpeg", "png", "tif", "tiff"}
        if format not in valid_formats:
            msg = f"Invalid format '{format}'. Valid formats: {', '.join(sorted(valid_formats))}"
            raise ValueError(msg)

        # Bit depth validation
        valid_bit_depths = {0, 8, 16}
        if bit_depth not in valid_bit_depths:
            msg = f"Invalid bit depth '{bit_depth}'. Valid values: {', '.join(map(str, sorted(valid_bit_depths)))}"
            raise ValueError(msg)

    def _setup_video_ai_environment(self) -> None:
        """Set up required environment variables for Video AI."""

        # Set model directories
        if platform.system() == "Darwin":  # macOS
            model_dir = "/Applications/Topaz Video AI.app/Contents/Resources/models"
            data_dir = os.path.expanduser("~/Library/Application Support/Topaz Labs LLC/Topaz Video AI/")
        else:  # Windows
            model_dir = "C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\models"
            data_dir = os.path.expanduser("~/AppData/Local/Topaz Labs LLC/Topaz Video AI/")

        os.environ["TVAI_MODEL_DIR"] = model_dir
        os.environ["TVAI_MODEL_DATA_DIR"] = data_dir

        logger.debug(f"Set TVAI_MODEL_DIR: {model_dir}")
        logger.debug(f"Set TVAI_MODEL_DATA_DIR: {data_dir}")

        # Validate authentication file
        self._validate_video_ai_auth(data_dir)

    def _validate_video_ai_auth(self, data_dir: str) -> None:
        """Validate Video AI authentication file exists and is valid."""
        import json
        import time

        # Check multiple possible auth file locations and formats
        auth_files = [
            # User data directory locations
            Path(data_dir) / "auth.tpz",
            Path(data_dir) / "auth.json",
            Path(data_dir) / "login.json",
            Path(data_dir) / "user.json",
            Path(data_dir) / ".auth",
            # Application bundle locations (actual location found by user)
            Path("/Applications/Topaz Video AI.app/Contents/Resources/models/auth.tpz"),
            Path("/Applications/Topaz Video AI.app/Contents/Resources/auth.tpz"),
        ]

        auth_found = False
        for auth_file in auth_files:
            if auth_file.exists():
                auth_found = True
                logger.debug(f"Found Video AI auth file: {auth_file}")

                try:
                    # Try to read and parse auth file
                    with open(auth_file) as f:
                        auth_data = json.load(f)

                    # Check if token exists and is not expired
                    if "token" not in auth_data:
                        logger.debug("Video AI authentication token missing in this file")
                        continue

                    # Check expiration if available
                    if "expires" in auth_data:
                        expires_timestamp = auth_data["expires"]
                        current_time = int(time.time())

                        if current_time >= expires_timestamp:
                            logger.debug("Video AI authentication token expired in this file")
                            continue

                        # Calculate time until expiration
                        time_remaining = expires_timestamp - current_time
                        days_remaining = time_remaining // (24 * 3600)

                        if days_remaining < 7:
                            logger.warning(
                                f"Video AI authentication expires in {days_remaining} days - consider refreshing"
                            )
                        else:
                            logger.debug(f"Video AI authentication valid for {days_remaining} days")

                    logger.debug("Video AI authentication validated successfully")
                    return

                except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                    logger.debug(f"Video AI authentication file {auth_file} invalid: {e}")
                    continue

        # If we found auth files but none were valid, show a warning
        # If no auth files found at all, show a more informative message
        if auth_found:
            logger.warning("Video AI authentication files found but none are valid - you may need to login via the GUI")
        else:
            logger.info(
                "Video AI authentication files not found - this is normal if you're logged in via GUI. Processing will continue."
            )
            logger.debug(f"Checked auth file locations: {[str(f) for f in auth_files]}")

    def _validate_video_ai_params(
        self,
        model: str,
        scale: int,
        fps: int | None,
        codec: str,
        quality: int,
        denoise: int | None,
        details: int | None,
        halo: int | None,
        blur: int | None,
        compression: int | None,
        device: int,
    ) -> None:
        """Validate Video AI parameters."""
        # Valid models
        valid_models = {
            "amq-13",
            "ahq-10",
            "ahq-11",
            "ahq-12",
            "alq-10",
            "alq-12",
            "alq-13",
            "alqs-1",
            "alqs-2",
            "amqs-1",
            "amqs-2",
            "aaa-9",
            "aaa-10",
            "prob-2",
            "prap-2",
            "ddv-1",
            "ddv-2",
            "ddv-3",
            "dtd-1",
            "dtd-3",
            "dtd-4",
            "dtds-1",
            "dtds-2",
            "dtv-1",
            "dtv-3",
            "dtv-4",
            "dtvs-1",
            "dtvs-2",
            "gcg-5",
            "ghq-5",
            "thd-3",
            "thf-4",
            "apo-8",
            "apf-1",
            "chr-1",
            "chr-2",
            "chf-1",
            "chf-2",
            "chf-3",
            "cpe-1",
            "cpe-2",
            "ref-2",
        }
        if model not in valid_models:
            msg = f"Invalid model '{model}'. Valid models: {', '.join(sorted(valid_models))}"
            raise ValueError(msg)

        # Scale validation
        if scale < 1 or scale > 4:
            msg = "Scale must be between 1 and 4 for Video AI"
            raise ValueError(msg)

        # Parameter range validations
        for param_name, param_value, min_val, max_val in [
            ("fps", fps, 1, 240),
            ("quality", quality, 1, 51),
            ("denoise", denoise, 0, 100),
            ("details", details, -100, 100),
            ("halo", halo, 0, 100),
            ("blur", blur, 0, 100),
            ("compression", compression, 0, 100),
            ("device", device, -1, 10),
        ]:
            if param_value is not None and (param_value < min_val or param_value > max_val):
                msg = f"{param_name} must be between {min_val} and {max_val}"
                raise ValueError(msg)

    def _build_video_ai_command(
        self,
        input_file: Path,
        output_file: Path,
        model: str,
        scale: int,
        fps: int | None,
        codec: str,
        quality: int,
        denoise: int | None,
        details: int | None,
        halo: int | None,
        blur: int | None,
        compression: int | None,
        stabilize: bool,
        interpolate: bool,
        custom_filters: str | None,
        device: int,
    ) -> list[str]:
        """Build FFmpeg command for Video AI processing."""
        cmd = [self._video_ai_ffmpeg, "-hide_banner", "-nostdin", "-y"]

        # Hardware acceleration
        if platform.system() == "Darwin":
            cmd.extend(["-strict", "2", "-hwaccel", "auto"])

        # Input
        cmd.extend(["-i", str(input_file)])

        # Build filter chain
        filters = []

        # Main upscaling filter
        upscale_filter = f"tvai_up=model={model}:scale={scale}"
        if denoise is not None:
            upscale_filter += f":denoise={denoise}"
        if details is not None:
            upscale_filter += f":details={details}"
        if halo is not None:
            upscale_filter += f":halo={halo}"
        if blur is not None:
            upscale_filter += f":blur={blur}"
        if compression is not None:
            upscale_filter += f":compression={compression}"
        if device >= 0:
            upscale_filter += f":device={device}"

        filters.append(upscale_filter)

        # Frame interpolation
        if interpolate and fps:
            filters.append(f"tvai_fi=model=chr-2:fps={fps}")

        # Custom filters
        if custom_filters:
            filters.append(custom_filters)

        # Add filter chain to command
        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        # Codec and encoding options
        if codec == "hevc_videotoolbox":
            cmd.extend(["-c:v", "hevc_videotoolbox", "-profile:v", "main"])
            cmd.extend(["-pix_fmt", "yuv420p", "-allow_sw", "1"])
        elif codec == "hevc_nvenc":
            cmd.extend(["-c:v", "hevc_nvenc", "-profile", "main", "-preset", "medium"])
            cmd.extend(["-pix_fmt", "yuv420p", "-movflags", "frag_keyframe+empty_moov"])
        elif codec == "hevc_amf":
            cmd.extend(["-c:v", "hevc_amf", "-profile", "main"])
            cmd.extend(["-pix_fmt", "yuv420p", "-movflags", "frag_keyframe+empty_moov"])
        else:
            # Default software encoding
            cmd.extend(["-c:v", "libx265", "-preset", "medium", "-pix_fmt", "yuv420p"])

        # Quality setting
        cmd.extend(["-crf", str(quality)])

        # Output file
        cmd.append(str(output_file))

        return cmd

    def _validate_photo_ai_params(
        self, format: str, quality: int, compression: int, bit_depth: int, tiff_compression: str
    ) -> None:
        """Validate Photo AI parameters."""
        # Format validation
        valid_formats = {"preserve", "jpg", "jpeg", "png", "tif", "tiff", "dng"}
        if format not in valid_formats:
            msg = f"Invalid format '{format}'. Valid formats: {', '.join(sorted(valid_formats))}"
            raise ValueError(msg)

        # Parameter range validations
        if quality < 0 or quality > 100:
            msg = "Quality must be between 0 and 100"
            raise ValueError(msg)

        if compression < 0 or compression > 10:
            msg = "PNG compression must be between 0 and 10"
            raise ValueError(msg)

        if bit_depth not in [8, 16]:
            msg = "TIFF bit depth must be 8 or 16"
            raise ValueError(msg)

        # TIFF compression validation
        valid_tiff_compression = {"none", "lzw", "zip"}
        if tiff_compression not in valid_tiff_compression:
            msg = f"Invalid TIFF compression '{tiff_compression}'. Valid values: {', '.join(sorted(valid_tiff_compression))}"
            raise ValueError(msg)

    def gp(
        self,
        input_path: str,
        model: str = "std",
        scale: int = 2,
        denoise: int | None = None,
        sharpen: int | None = None,
        compression: int | None = None,
        detail: int | None = None,
        creativity: int | None = None,
        texture: int | None = None,
        prompt: str | None = None,
        face_recovery: int | None = None,
        face_recovery_version: int = 2,
        format: str = "preserve",
        quality: int = 95,
        bit_depth: int = 0,
        parallel_read: int = 1,
        output: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Process images using Topaz Gigapixel AI.

        Args:
            input_path: Path to input image(s) or directory
            model: AI model to use (std, hf, low, art, lines, recovery, redefine, etc.)
            scale: Upscale factor (1-6)
            denoise: Denoise strength (1-100)
            sharpen: Sharpen strength (1-100)
            compression: Compression reduction (1-100)
            detail: Detail enhancement (1-100)
            creativity: Creativity level for generative models (1-6)
            texture: Texture level for generative models (1-6)
            prompt: Text prompt for generative models
            face_recovery: Face recovery strength (1-100)
            face_recovery_version: Face recovery version (1 or 2)
            format: Output format (preserve, jpg, png, tiff)
            quality: JPEG quality (1-100)
            bit_depth: Bit depth (0=preserve, 8, 16)
            parallel_read: Parallel file loading (1-10)
            output: Output directory path

        Returns:
            True if processing succeeded, False otherwise

        """
        logger.info(f"Starting Gigapixel AI processing: {input_path}")

        # Validate parameters
        self._validate_gigapixel_params(
            model,
            scale,
            denoise,
            sharpen,
            compression,
            detail,
            creativity,
            texture,
            face_recovery,
            face_recovery_version,
            format,
            quality,
            bit_depth,
            parallel_read,
        )

        # Find Gigapixel executable
        if not self._gigapixel_exe:
            self._gigapixel_exe = self._find_executable("gigapixel")
            if not self._gigapixel_exe:
                msg = "Gigapixel AI executable not found"
                raise OSError(msg)

        # Validate paths
        input_path_obj, output_path_obj = self._validate_paths(input_path, output)

        # Build command arguments
        cmd = [self._gigapixel_exe, "--cli"]

        # Input/output
        cmd.extend(["-i", str(input_path_obj)])
        cmd.extend(["-o", str(output_path_obj)])
        cmd.extend(["--create-folder"])

        # Model and scale
        cmd.extend(["-m", model])
        cmd.extend(["--scale", str(scale)])

        # Optional parameters
        if denoise is not None:
            cmd.extend(["--denoise", str(denoise)])
        if sharpen is not None:
            cmd.extend(["--sharpen", str(sharpen)])
        if compression is not None:
            cmd.extend(["--compression", str(compression)])
        if detail is not None:
            cmd.extend(["--detail", str(detail)])
        if creativity is not None:
            cmd.extend(["--creativity", str(creativity)])
        if texture is not None:
            cmd.extend(["--texture", str(texture)])
        if prompt:
            cmd.extend(["--prompt", prompt])
        if face_recovery is not None:
            cmd.extend(["--face-recovery", str(face_recovery)])
            cmd.extend(["--face-recovery-version", str(face_recovery_version)])

        # Output format options
        cmd.extend(["-f", format])
        if format.lower() in ["jpg", "jpeg"]:
            cmd.extend(["--jpeg-quality", str(quality)])
        if bit_depth > 0:
            cmd.extend(["--bit-depth", str(bit_depth)])

        # Performance options
        if parallel_read > 1:
            cmd.extend(["-p", str(parallel_read)])

        # Processing options
        if input_path_obj.is_dir():
            cmd.append("--recursive")
        if self.verbose:
            cmd.append("--verbose")

        # Execute command with progress monitoring
        try:
            if self.verbose and not self.dry_run:
                returncode, stdout, stderr = self._execute_command_with_progress(cmd, "Gigapixel AI")
            else:
                returncode, stdout, stderr = self._execute_command(cmd)

            if returncode == 0:
                logger.success("Gigapixel AI processing completed successfully")
                return True
            logger.error(f"Gigapixel AI processing failed (code {returncode}): {stderr}")
            return False

        except Exception as e:
            logger.error(f"Gigapixel AI processing error: {e}")
            return False

    def video(
        self,
        input_path: str,
        model: str = "amq-13",
        scale: int = 2,
        fps: int | None = None,
        codec: str = "hevc_videotoolbox",
        quality: int = 18,
        denoise: int | None = None,
        details: int | None = None,
        halo: int | None = None,
        blur: int | None = None,
        compression: int | None = None,
        stabilize: bool = False,
        interpolate: bool = False,
        custom_filters: str | None = None,
        device: int = 0,
        output: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Process videos using Topaz Video AI.

        Args:
            input_path: Path to input video file
            model: AI model to use (amq-13, prob-2, etc.)
            scale: Upscale factor (1-4)
            fps: Target frame rate for interpolation
            codec: Video codec (hevc_videotoolbox, hevc_nvenc, etc.)
            quality: Video quality/CRF value
            denoise: Denoise strength
            details: Detail enhancement
            halo: Halo reduction
            blur: Blur reduction
            compression: Compression artifact reduction
            stabilize: Enable stabilization
            interpolate: Enable frame interpolation
            custom_filters: Custom FFmpeg filters
            device: GPU device index
            output: Output file path

        Returns:
            True if processing succeeded, False otherwise

        """
        logger.info(f"Starting Video AI processing: {input_path}")

        # Find Video AI FFmpeg
        if not self._video_ai_ffmpeg:
            self._video_ai_ffmpeg = self._find_executable("video_ai")
            if not self._video_ai_ffmpeg:
                msg = "Video AI FFmpeg not found"
                raise OSError(msg)

        # Set up Video AI environment variables
        self._setup_video_ai_environment()

        # Validate parameters
        self._validate_video_ai_params(
            model, scale, fps, codec, quality, denoise, details, halo, blur, compression, device
        )

        # Validate paths
        input_path_obj, output_path_obj = self._validate_paths(input_path, output)
        if input_path_obj.is_dir():
            msg = "Video AI only supports single video files, not directories"
            raise ValueError(msg)

        # Determine output filename
        if output_path_obj.is_dir():
            output_file = output_path_obj / f"{input_path_obj.stem}_processed{input_path_obj.suffix}"
        else:
            output_file = output_path_obj

        # Build FFmpeg command
        cmd = self._build_video_ai_command(
            input_path_obj,
            output_file,
            model,
            scale,
            fps,
            codec,
            quality,
            denoise,
            details,
            halo,
            blur,
            compression,
            stabilize,
            interpolate,
            custom_filters,
            device,
        )

        # Execute command
        try:
            returncode, stdout, stderr = self._execute_command(cmd)

            if returncode == 0:
                logger.success("Video AI processing completed successfully")
                return True
            logger.error(f"Video AI processing failed (code {returncode}): {stderr}")
            return False

        except Exception as e:
            logger.error(f"Video AI processing error: {e}")
            return False

    def photo(
        self,
        input_path: str,
        autopilot_preset: str = "default",
        format: str = "preserve",
        quality: int = 95,
        compression: int = 2,
        bit_depth: int = 16,
        tiff_compression: str = "zip",
        show_settings: bool = False,
        skip_processing: bool = False,
        override_autopilot: bool = False,
        upscale: bool | None = None,
        noise: bool | None = None,
        sharpen: bool | None = None,
        lighting: bool | None = None,
        color: bool | None = None,
        output: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Process images using Topaz Photo AI.

        Args:
            input_path: Path to input image(s) or directory
            autopilot_preset: Autopilot preset to use
            format: Output format (preserve, jpg, png, tiff, dng)
            quality: JPEG quality (0-100)
            compression: PNG compression (0-10)
            bit_depth: TIFF bit depth (8 or 16)
            tiff_compression: TIFF compression (none, lzw, zip)
            show_settings: Show Autopilot settings before processing
            skip_processing: Skip processing (just show settings)
            override_autopilot: Override Autopilot with manual settings
            upscale: Enable/disable upscale enhancement
            noise: Enable/disable denoise enhancement
            sharpen: Enable/disable sharpen enhancement
            lighting: Enable/disable lighting adjustment
            color: Enable/disable color balance
            output: Output directory path

        Returns:
            True if processing succeeded, False otherwise

        """
        logger.info(f"Starting Photo AI processing: {input_path}")

        # Find Photo AI executable
        if not self._photo_ai_exe:
            self._photo_ai_exe = self._find_executable("photo_ai")
            if not self._photo_ai_exe:
                msg = "Photo AI executable not found"
                raise OSError(msg)

        # Validate parameters
        self._validate_photo_ai_params(format, quality, compression, bit_depth, tiff_compression)

        # Validate paths
        input_path_obj, output_path_obj = self._validate_paths(input_path, output)

        # Build command arguments
        cmd = [self._photo_ai_exe, "--cli"]

        # Input/output
        cmd.extend(["-i", str(input_path_obj)])
        cmd.extend(["-o", str(output_path_obj)])

        # Format options
        cmd.extend(["-f", format])
        if format.lower() in ["jpg", "jpeg"]:
            cmd.extend(["-q", str(quality)])
        elif format.lower() == "png":
            cmd.extend(["-c", str(compression)])
        elif format.lower() in ["tif", "tiff"]:
            cmd.extend(["-d", str(bit_depth)])
            cmd.extend(["-tc", tiff_compression])

        # Debug options
        if show_settings:
            cmd.append("--showSettings")
        if skip_processing:
            cmd.append("--skipProcessing")
        if self.verbose:
            cmd.append("--verbose")

        # Processing options
        if input_path_obj.is_dir():
            cmd.append("--recursive")

        # Experimental settings override
        if override_autopilot:
            cmd.append("--override")

            if upscale is not None:
                if upscale:
                    cmd.append("--upscale")
                else:
                    cmd.extend(["--upscale", "enabled=false"])
            if noise is not None:
                if noise:
                    cmd.append("--noise")
                else:
                    cmd.extend(["--noise", "enabled=false"])
            if sharpen is not None:
                if sharpen:
                    cmd.append("--sharpen")
                else:
                    cmd.extend(["--sharpen", "enabled=false"])
            if lighting is not None:
                if lighting:
                    cmd.append("--lighting")
                else:
                    cmd.extend(["--lighting", "enabled=false"])
            if color is not None:
                if color:
                    cmd.append("--color")
                else:
                    cmd.extend(["--color", "enabled=false"])

        # Execute command with batch handling for directories
        try:
            if input_path_obj.is_dir():
                return self._execute_photo_ai_batch(cmd, input_path_obj)
            returncode, stdout, stderr = self._execute_command(cmd)
            return self._handle_photo_ai_result(returncode, stdout, stderr)

        except Exception as e:
            if self._handle_processing_error(e, "photo"):
                logger.info("Photo AI error recovery suggested - consider retrying with adjusted parameters")
            logger.error(f"Photo AI processing error: {e}")
            return False

    def _execute_photo_ai_batch(self, base_cmd: list[str], input_dir: Path) -> bool:
        """Execute Photo AI processing in batches to handle the ~450 image limit."""
        import glob

        # Find all supported image files
        image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.tiff", "*.tif", "*.bmp", "*.webp", "*.dng", "*.raw"]
        all_files = []

        for ext in image_extensions:
            all_files.extend(glob.glob(str(input_dir / "**" / ext), recursive=True))

        if not all_files:
            logger.warning("No supported image files found in directory")
            return False

        file_count = len(all_files)
        logger.info(f"Found {file_count} images to process")

        # Calculate optimal batch size (Photo AI limit is ~450 images)
        max_batch_size = 400  # Conservative limit
        optimal_batch = self._get_optimal_batch_size(file_count, "photo")
        batch_size = min(optimal_batch, max_batch_size)

        if file_count > batch_size:
            logger.info(f"Processing in batches of {batch_size} images")

        # Process in batches
        total_success = True
        processed_count = 0

        for i in range(0, file_count, batch_size):
            batch_files = all_files[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (file_count + batch_size - 1) // batch_size

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_files)} images)")

            # Create temporary directory for this batch

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create symlinks to batch files (to avoid copying large files)
                for file_path in batch_files:
                    file_obj = Path(file_path)
                    link_path = temp_path / file_obj.name

                    # Handle duplicate names by adding suffix
                    counter = 1
                    while link_path.exists():
                        name_parts = file_obj.stem, counter, file_obj.suffix
                        link_path = temp_path / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        counter += 1

                    try:
                        link_path.symlink_to(file_obj.resolve())
                    except OSError:
                        # Fallback to copying if symlink fails
                        import shutil

                        shutil.copy2(file_obj, link_path)

                # Update command for this batch
                batch_cmd = base_cmd.copy()
                # Replace input path with temp directory
                for idx, arg in enumerate(batch_cmd):
                    if arg == str(input_dir):
                        batch_cmd[idx] = str(temp_path)
                        break

                # Execute batch
                try:
                    returncode, stdout, stderr = self._execute_command(batch_cmd)
                    batch_success = self._handle_photo_ai_result(returncode, stdout, stderr, batch_num)

                    if batch_success:
                        processed_count += len(batch_files)
                    else:
                        total_success = False
                        logger.error(f"Batch {batch_num} failed")

                except Exception as e:
                    logger.error(f"Batch {batch_num} error: {e}")
                    total_success = False

        if total_success:
            logger.success(f"Photo AI batch processing completed: {processed_count}/{file_count} images processed")
        else:
            logger.warning(
                f"Photo AI batch processing completed with errors: {processed_count}/{file_count} images processed"
            )

        return total_success

    def _handle_photo_ai_result(self, returncode: int, stdout: str, stderr: str, batch_num: int | None = None) -> bool:
        """Handle Photo AI result codes with proper logging."""
        batch_prefix = f"Batch {batch_num}: " if batch_num else ""

        # Handle Photo AI specific return codes
        if returncode == 0:
            logger.success(f"{batch_prefix}Photo AI processing completed successfully")
            return True
        if returncode == 1:
            logger.warning(f"{batch_prefix}Photo AI processing completed with some failures")
            return True  # Partial success is still success
        if returncode == 255:  # -1
            logger.error(f"{batch_prefix}Photo AI: No valid files found")
            return False
        if returncode == 254:  # -2
            logger.error(f"{batch_prefix}Photo AI: Invalid log token - please open the app to login")
            return False
        if returncode == 253:  # -3
            logger.error(f"{batch_prefix}Photo AI: Invalid argument")
            return False

        logger.error(f"{batch_prefix}Photo AI processing failed (code {returncode}): {stderr}")
        return False

    def version(self) -> str:
        """Return topyaz version information."""
        return f"topyaz v{__version__}"

    def validate(
        self, check_licenses: bool = True, check_environment: bool = True, check_connectivity: bool = False
    ) -> dict[str, Any]:
        """
        Validate system setup and requirements.

        Args:
            check_licenses: Check license status for all products
            check_environment: Check system environment
            check_connectivity: Check network connectivity for remote hosts

        Returns:
            Validation results dictionary

        """
        results = {"system": {}, "licenses": {}, "connectivity": {}, "overall": True}

        # System validation
        if check_environment:
            logger.info("Validating system environment...")
            results["system"] = {
                "platform": platform.system(),
                "version": platform.version(),
                "memory_gb": psutil.virtual_memory().total / (1024**3),
                "disk_free_gb": psutil.disk_usage(Path.home()).free / (1024**3),
            }

        # License validation
        if check_licenses:
            logger.info("Validating licenses...")
            # TODO: Implement license checking
            results["licenses"] = {"gigapixel": "unknown", "video_ai": "unknown", "photo_ai": "unknown"}

        # Connectivity validation
        if check_connectivity and self.remote_host:
            logger.info("Validating connectivity...")
            # TODO: Implement connectivity checking
            results["connectivity"] = {"remote_host": self.remote_host, "reachable": False}

        return results

    def examples(self) -> None:
        """Show usage examples for all products."""

    def troubleshoot(self) -> None:
        """Run diagnostic checks and provide troubleshooting guidance."""
        logger.info("Running diagnostics...")

        # Check executables
        logger.info("Checking Topaz product installations...")
        products = ["gigapixel", "video_ai", "photo_ai"]
        for product in products:
            exe = self._find_executable(product)
            if exe:
                logger.success(f"✓ {product}: {exe}")
            else:
                logger.error(f"✗ {product}: Not found")

        # Check system resources
        memory_gb = psutil.virtual_memory().total / (1024**3)
        disk_gb = psutil.disk_usage(Path.home()).free / (1024**3)

        logger.info(f"System memory: {memory_gb:.1f}GB")
        logger.info(f"Free disk space: {disk_gb:.1f}GB")

        if memory_gb < 16:
            logger.warning("Consider upgrading to 16GB+ RAM for better performance")
        if disk_gb < 80:
            logger.warning("Free up disk space - Video AI requires ~80GB for models")

        # Check GPU information
        logger.info("Checking GPU resources...")
        gpu_info = self._get_gpu_info()

        if gpu_info["available"]:
            gpu_type = gpu_info.get("type", "unknown")
            device_count = gpu_info.get("count", 0)
            logger.success(f"✓ GPU: {device_count} {gpu_type.upper()} device(s) detected")

            for i, device in enumerate(gpu_info["devices"]):
                device_name = device.get("name", f"GPU {i}")
                logger.info(f"  - {device_name}")

                if "memory_total_mb" in device:
                    total_mem = device["memory_total_mb"] / 1024
                    used_mem = device.get("memory_used_mb", 0) / 1024
                    logger.info(f"    Memory: {used_mem:.1f}GB / {total_mem:.1f}GB")

                if "utilization_percent" in device:
                    util = device["utilization_percent"]
                    logger.info(f"    Utilization: {util}%")

                if "temperature_c" in device:
                    temp = device["temperature_c"]
                    if temp > 0:
                        logger.info(f"    Temperature: {temp}°C")
        else:
            logger.warning("✗ No compatible GPU detected")
            if gpu_info["errors"]:
                for error in gpu_info["errors"]:
                    logger.debug(f"GPU detection error: {error}")

        logger.info("Diagnostics complete")
