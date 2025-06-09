from pathlib import Path
import shutil
import tempfile
from loguru import logger
from topyaz.core.errors import ProcessingError


class PhotoAIBatch:
    # Photo AI has a hard limit of ~450 images per batch
    MAX_BATCH_SIZE = 400  # Conservative limit

    def __init__(self, product_instance):
        self.product = product_instance
        self.executor = product_instance.executor
        self.options = product_instance.options

    def process_batch_directory(self, input_dir: Path, output_dir: Path, **kwargs) -> list[dict[str, any]]:
        """
        Process directory with Photo AI's 450 image batch limit handling.
        """
        image_files = self._find_image_files(input_dir)
        if not image_files:
            logger.warning(f"No supported image files found in {input_dir}")
            return []

        logger.info(f"Found {len(image_files)} images to process")
        batches = [image_files[i : i + self.MAX_BATCH_SIZE] for i in range(0, len(image_files), self.MAX_BATCH_SIZE)]
        logger.info(f"Processing {len(batches)} batch(es) of up to {self.MAX_BATCH_SIZE} images each")

        results = []
        for batch_num, batch_files in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)} ({len(batch_files)} images)")
            try:
                result = self._process_single_batch(batch_files, output_dir, batch_num, **kwargs)
                results.append(result)
                if not result.get("success", False):
                    logger.error(f"Batch {batch_num} failed")
                    break
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                results.append(
                    {"batch_num": batch_num, "success": False, "error": str(e), "files_count": len(batch_files)}
                )
                break
        return results

    def _find_image_files(self, input_dir: Path) -> list[Path]:
        image_files = []
        for ext in self.product.supported_formats:
            image_files.extend(input_dir.rglob(f"*.{ext}"))
            image_files.extend(input_dir.rglob(f"*.{ext.upper()}"))
        return list(set(image_files))

    def _process_single_batch(
        self, batch_files: list[Path], output_dir: Path, batch_num: int, **kwargs
    ) -> dict[str, any]:
        with tempfile.TemporaryDirectory(prefix=f"topyaz_batch_{batch_num}_") as temp_dir:
            temp_path = Path(temp_dir)
            batch_input_dir = temp_path / "input"
            batch_input_dir.mkdir()

            for file_path in batch_files:
                target_path = batch_input_dir / file_path.name
                try:
                    target_path.symlink_to(file_path)
                except OSError:
                    shutil.copy2(file_path, target_path)

            cmd = self.product.build_command(batch_input_dir, output_dir, **kwargs)
            try:
                exit_code, stdout, stderr = self.executor.execute(cmd, timeout=self.options.timeout)
                success = self._handle_photo_ai_result(exit_code, stdout, stderr, batch_num)
                return {
                    "batch_num": batch_num,
                    "success": success,
                    "exit_code": exit_code,
                    "files_count": len(batch_files),
                    "stdout": stdout,
                    "stderr": stderr,
                }
            except Exception as e:
                logger.error(f"Batch {batch_num} execution failed: {e}")
                return {
                    "batch_num": batch_num,
                    "success": False,
                    "error": str(e),
                    "files_count": len(batch_files),
                }

    def _handle_photo_ai_result(self, exit_code: int, stdout: str, stderr: str, batch_num: int) -> bool:
        if exit_code == 0:
            logger.info(f"Batch {batch_num} completed successfully")
            return True
        if exit_code == 1:
            logger.warning(f"Batch {batch_num} completed with some failures (partial success)")
            return True
        if exit_code == 255:
            logger.error(f"Batch {batch_num} failed: No valid files found")
            return False
        if exit_code == 254:
            logger.error(f"Batch {batch_num} failed: Invalid log token - login required")
            raise ProcessingError("Photo AI authentication required. Please log in via the Photo AI GUI.")
        if exit_code == 253:
            logger.error(f"Batch {batch_num} failed: Invalid argument")
            if stderr:
                logger.error(f"Error details: {stderr}")
            return False
        logger.error(f"Batch {batch_num} failed with exit code {exit_code}")
        if stderr:
            logger.error(f"Error details: {stderr}")
        return False
