#!/bin/bash
set -e

echo "🚀 voria Installation Script"
echo "=============================="

# Check prerequisites
echo ""
echo "[1/4] Checking prerequisites..."

if ! command -v rustc &> /dev/null; then
    echo "❌ Rust not found. Install from https://rustup.rs"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git"
    exit 1
fi

echo "✓ All prerequisites installed"
echo "   Rust: $(rustc --version)"
echo "   Python: $(python3 --version)"
echo "   Git: $(git --version)"

# Build Rust CLI
echo ""
echo "[2/4] Building Rust CLI..."
cargo build --release
RUST_BINARY=$(pwd)/target/release/voria
echo "✓ Built: $RUST_BINARY"

# Setup Python virtual environment
echo ""
echo "[3/4] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

cd python
pip install -e . > /dev/null 2>&1
cd ..
echo "✓ Python environment ready"

# Create symlink or wrapper
echo ""
echo "[4/4] Setting up CLI symlink..."
mkdir -p ~/.local/bin
ln -sf "$RUST_BINARY" ~/.local/bin/voria
echo "✓ CLI ready at ~/.local/bin/voria"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Add ~/.local/bin to your PATH (if not already)"
echo "  2. Run: voria --help"
echo "  3. Try: voria plan 1"
echo ""
echo "For more info, see:"
echo "  - README.md"
echo "  - docs/ARCHITECTURE.md"
echo "  - docs/IPC_PROTOCOL.md"
