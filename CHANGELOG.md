# 📋 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-07-14

### Added
- 🎨 **OpenAI DALL-E 3 Image Generation**: Automatic high-quality AI image generation for articles
- 🖼️ **Featured Image Auto-Generation**: 1792x1024 HD quality article header images
- 📊 **Section Image Auto-Generation**: 1024x1024 specialized images for each article section (8 images)
- 🔗 **WordPress Complete Integration**: Automatic image upload and embedding in articles
- 🧹 **Clean Article Output**: Automatic removal of system credits for professional appearance
- 📝 **Enhanced Article Templates**: Professional article structure with image placeholders

### Improved
- **Article Quality**: Increased from 2,775 to 4,291 characters (55% improvement)
- **Visual Appeal**: Articles now include 9 high-quality AI-generated images
- **WordPress Integration**: Seamless image uploading and proper WordPress block formatting
- **Cost Efficiency**: $0.40 per article for enterprise-grade content with images

### Fixed
- Image display issues in WordPress
- Featured image automatic assignment
- Article formatting and clean output

### Technical
- Added `src/generators/image_generator.py` - DALL-E 3 image generation engine
- Added `run_image_article_generator.py` - Main script for image-enabled article generation
- Added `debug_and_fix_images.py` - Image display troubleshooting tool
- Added `IMAGE_GENERATION_GUIDE.md` - Comprehensive image generation documentation
- Updated WordPress client with media upload capabilities
- Enhanced error handling for image generation and upload processes

## [2.0.0] - 2025-07-03

### Added
- 🎉 **4000-Character Article Generation**: Detailed 8-section article structure
- 🎯 **Complete SEO Optimization**: Focus keywords, meta descriptions, and tags
- 🎪 **Interactive Candidate Selection**: 10 article candidates with star ratings
- 📊 **High-Quality News Collection**: 7 major crypto news sources
- 📤 **WordPress Auto-Publishing**: REST API integration with SEO metadata

### Improved
- **Article Length**: Increased from 1,891 to 4,407 characters (2.3x improvement)
- **Importance Scoring**: Enhanced to 100-point scale
- **Article Candidates**: Expanded from 3 to 10 options
- **SEO Compliance**: Complete metadata optimization

### Technical
- Enhanced Claude generator with 8-section article structure
- Improved RSS parser with intelligent scoring
- WordPress client with full REST API support
- Advanced news categorization system

## [1.0.0] - 2025-07-02

### Added
- 📝 **Basic Article Generation**: Simple crypto news article creation
- 🔗 **WordPress Integration**: Basic publishing functionality
- 📊 **News Collection**: RSS feed parsing from major crypto sources
- 🏗️ **Core Architecture**: Modular system design

### Technical
- Initial project structure
- Basic RSS parsing capabilities
- Simple WordPress XML-RPC integration
- Core article generation templates

---

**Legend:**
- 🎨 New Feature
- 🔧 Enhancement  
- 🐛 Bug Fix
- 📝 Documentation
- 🔒 Security
- ⚡ Performance