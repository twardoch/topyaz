# topyaz: Unified CLI Wrapper for Topaz Labs Products

**topyaz** is a Python CLI wrapper that unifies Topaz Labs' three AI products (Video AI, Gigapixel AI, Photo AI) into a single command-line interface for professional batch processing workflows.

**🎯 Core Purpose:**

- Single CLI tool for all Topaz products instead of using separate GUIs
- Batch operations with progress monitoring and error recovery

**📋 Requirements:**

- macOS 11+ (Topaz products are Mac-focused)
- Gigapixel AI Pro license ($499/year) for CLI access
- 16GB+ RAM, 80GB+ storage for models

**✅ Current Status:**

- **Phase 1 Complete**: Comprehensive refactoring from monolithic to modular architecture
- **Implementation**: Clean, production-ready codebase with 18+ focused modules
- **Architecture**: Modular design with dependency injection, abstract interfaces, and excellent testability

**💡 Key Value:**

- ~2x faster than GUI for batch operations
- Unified interface across Video AI (upscaling), Gigapixel AI (image enhancement), Photo AI (auto-enhancement)
- Production-ready error handling and recovery mechanisms

**Target Users:** Video/photo professionals, content creators, automated workflow developers who need efficient batch processing of large media collections.

## ✨ Features

- **🎯 Unified Interface**: Single command-line tool for all three Topaz products
- **🔄 Batch Processing**: Intelligent batch operations with progress monitoring
- **🛡️ Failsafe Design**: Comprehensive error handling and recovery mechanisms
- **📊 Progress Tracking**: Real-time progress with ETA calculations
- **⚙️ Hardware Optimization**: Automatic detection and optimization for your system
- **🔧 Flexible Configuration**: YAML-based configuration with preset workflows

## 🚀 Quick Start

### Installation

```bash
pip install topyaz
```

### Basic Usage

```bash
# Upscale a video using Video AI
topyaz video input.mp4 --scale 2 --model amq-13

# Batch upscale images with Gigapixel AI (Pro license required)
topyaz giga photos/ --scale 4 --model recovery --denoise 40

# Enhance photos with Photo AI Autopilot
topyaz photo raw_photos/ --format_output jpg --quality_output 95
```

## 📋 Requirements

### System Requirements

- **macOS**: 11.0 Big Sur or higher
  - macOS 13 Ventura+ for advanced Video AI models (Rhea, Aion)
  - macOS 14 Sonoma+ for Gigapixel AI generative models
- **Python**: 3.8 or higher
- **Memory**: 16GB RAM minimum (32GB recommended for 4K video)
- **Storage**: 80GB+ free space for Video AI models
- **GPU**: 2GB+ VRAM for GPU acceleration

### Topaz Products

- **Topaz Video AI**: Any valid license
- **Topaz Gigapixel AI**: Pro license required for CLI access ($499/year)
- **Topaz Photo AI**: Any valid license

## 🔧 Configuration

Create a configuration file at `~/.topyaz/config.yaml`:

```yaml
defaults:
  output_dir: '~/processed'
  preserve_structure: true
  backup_originals: false
  log_level: 'INFO'

video:
  default_model: 'amq-13'
  default_codec: 'hevc_videotoolbox'
  default_quality: 18

_gigapixel:
  default_model: 'std'
  default_format: 'preserve'
  parallel_read: 4

photo:
  default_format: 'jpg'
  default_quality: 95
```

## 📖 Documentation

### Video AI Processing

```bash
# Basic upscaling
topyaz video input.mp4 --scale 2 --model amq-13

# Advanced processing with stabilization and interpolation
topyaz video shaky_video.mp4 \
    --stabilize \
    --scale 2 \
    --interpolate \
    --fps 60 \
    --denoise 50

# Batch processing with custom output
topyaz video videos/ \
    --scale 2 \
    --model prob-3 \
    --output-dir ./enhanced \
    --recursive
```

**Supported Models:**

- **Artemis**: amq-13, ahq-10/11/12, alq-10/12/13, alqs-1/2, amqs-1/2, aaa-9/10
- **Proteus**: prob-2, prap-2
- **Dione**: ddv-1/2/3, dtd-1/3/4, dtds-1/2, dtv-1/3/4, dtvs-1/2
- **Gaia**: gcg-5, ghq-5
- **Theia**: thd-3, thf-4
- **Interpolation**: chr-1/2, chf-1/2/3, apo-8, apf-1

### Gigapixel AI Processing

```bash
# Standard upscaling
topyaz giga images/ --scale 4 --model std

# Art & CG optimization
topyaz giga artwork/ --scale 2 --model art --sharpen 30

# Generative upscaling with prompts
topyaz giga photos/ \
    --model redefine \
    --scale 2 \
    --creativity 4 \
    --texture 3 \
    --prompt "high resolution portrait photography"

# Face recovery enhancement
topyaz giga portraits/ \
    --scale 2 \
    --model recovery \
    --face-recovery 80 \
    --face-recovery-creativity 1
```

**Available Models:**

- **Standard**: std, hf (high fidelity), low (low resolution)
- **Specialized**: art/cg (Art & CG), lines, text, vc (very compressed)
- **Recovery**: recovery (with face enhancement)
- **Generative**: redefine (with AI prompts)

### Photo AI Processing

```bash
# Autopilot enhancement
topyaz photo raw_photos/ --format_output jpg --quality_output 95

# Custom format_output conversion
topyaz photo images/ \
    --format_output tiff \
    --bit-depth 16 \
    --tiff-compression zip

# Show current Autopilot settings
topyaz photo test_image.jpg --show-settings --skip-processing
```

## 🔒 Security

- Command injection prevention
- Audit logging for all operations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Topaz Labs](https://www.topazlabs.com/) for their excellent AI-powered tools
- Community contributors and tool developers
- Beta testers and early adopters

## 📞 Support

- **Documentation**: [docs.topyaz.org](https://docs.topyaz.org)
- **Issues**: [GitHub Issues](https://github.com/username/topyaz/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/topyaz/discussions)
- **Community**: [Topaz Labs Community](https://community.topazlabs.com/)

---

**Note**: This project is not officially affiliated with Topaz Labs. It's a community-driven wrapper around their CLI tools.
