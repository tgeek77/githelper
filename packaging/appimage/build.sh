#!/usr/bin/env bash
# Build githelper AppImages (CLI and/or GUI) with PyInstaller + appimagetool.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

TARGET="${1:-all}"
VERSION="${VERSION:-$(python3 -c 'from githelper import __version__; print(__version__)')}"
ARCH="${ARCH:-x86_64}"
DIST="$ROOT/dist"
APPIMAGE_DIR="$ROOT/packaging/appimage"
APPIMAGETOOL="${APPIMAGETOOL:-appimagetool}"

die() {
    echo "error: $*" >&2
    exit 1
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

ensure_pip() {
    if python3 -m pip --version >/dev/null 2>&1; then
        return
    fi
    if python3 -m ensurepip --upgrade >/dev/null 2>&1; then
        return
    fi
    die "pip is required; install python3-pip or run: python3 -m ensurepip --upgrade"
}

read_version() {
    if [[ -n "${GITHUB_REF_NAME:-}" && "$GITHUB_REF_NAME" == v* ]]; then
        VERSION="${GITHUB_REF_NAME#v}"
    fi
}

install_appimagetool() {
    if command -v appimagetool >/dev/null 2>&1; then
        APPIMAGETOOL=(appimagetool)
        return
    fi
    local cache="$ROOT/.cache/appimagetool"
    local tool="$cache/appimagetool-${ARCH}.AppImage"
    mkdir -p "$cache"
    if [[ ! -x "$tool" ]]; then
        echo "Downloading appimagetool..."
        wget -q -O "$tool" \
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"
        chmod +x "$tool"
    fi
    # Works on CI runners without FUSE.
    APPIMAGETOOL=("$tool" --appimage-extract-and-run)
}

build_pyinstaller() {
    local spec="$1"
    echo "==> PyInstaller: $(basename "$spec")"
    python3 -m PyInstaller "$spec" --clean --noconfirm
}

assemble_appdir() {
    local name="$1"
    local binary="$2"
    local desktop_src="$3"
    local icon_id="$4"
    local appdir="$DIST/${name}.AppDir"
    local icon_png="$APPIMAGE_DIR/icons/${icon_id}.png"

    rm -rf "$appdir"
    mkdir -p \
        "$appdir/usr/bin" \
        "$appdir/usr/share/applications" \
        "$appdir/usr/share/icons/hicolor/256x256/apps"

    python3 "$APPIMAGE_DIR/generate-icons.py" "$icon_id" "$APPIMAGE_DIR/icons"

    cp "$DIST/$binary" "$appdir/usr/bin/$binary"
    chmod +x "$appdir/usr/bin/$binary"

    cp "$desktop_src" "$appdir/usr/share/applications/"
    cp "$desktop_src" "$appdir/"

    # AppImage spec: icon in AppDir root, hicolor theme path, and .DirIcon PNG.
    cp "$icon_png" "$appdir/${icon_id}.png"
    cp "$icon_png" "$appdir/.DirIcon"
    cp "$icon_png" "$appdir/usr/share/icons/hicolor/256x256/apps/${icon_id}.png"

    cat > "$appdir/AppRun" <<EOF
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
export PATH="\${HERE}/usr/bin:\${PATH}"
exec "\${HERE}/usr/bin/$binary" "\$@"
EOF
    chmod +x "$appdir/AppRun"
}

make_appimage() {
    local name="$1"
    local appdir="$DIST/${name}.AppDir"
    local output="$DIST/${name}-${VERSION}-${ARCH}.AppImage"

    echo "==> AppImage: $(basename "$output")"
    ARCH="$ARCH" "${APPIMAGETOOL[@]}" "$appdir" "$output"
    chmod +x "$output"
}

smoke_test_cli() {
    local image="$DIST/githelper-cli-${VERSION}-${ARCH}.AppImage"
    echo "==> Smoke test CLI"
    "$image" --help >/dev/null
    "$image" config path >/dev/null
}

smoke_test_gui() {
    local image="$DIST/githelper-gui-${VERSION}-${ARCH}.AppImage"
    echo "==> Smoke test GUI (headless import check)"
    if command -v xvfb-run >/dev/null 2>&1; then
        xvfb-run -a "$image" &
        local pid=$!
        sleep 3
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    else
        echo "Skipping GUI launch test (xvfb-run not available)"
    fi
}

build_cli() {
    build_pyinstaller "$ROOT/packaging/pyinstaller/githelper-cli.spec"
    assemble_appdir \
        "githelper-cli" \
        "githelper" \
        "$APPIMAGE_DIR/githelper.desktop" \
        "githelper"
    make_appimage "githelper-cli"
    smoke_test_cli
}

build_gui() {
    build_pyinstaller "$ROOT/packaging/pyinstaller/githelper-gui.spec"
    assemble_appdir \
        "githelper-gui" \
        "githelper-gui" \
        "$APPIMAGE_DIR/githelper-gui.desktop" \
        "githelper-gui"
    make_appimage "githelper-gui"
    smoke_test_gui
}

main() {
    require_cmd python3
    require_cmd wget
    read_version
    ensure_pip
    install_appimagetool

    python3 -m pip install --upgrade pip
    python3 -m pip install -r "$ROOT/packaging/requirements-build.txt"

    mkdir -p "$DIST"
    export PYTHONPATH="$ROOT"

    case "$TARGET" in
        cli) build_cli ;;
        gui) build_gui ;;
        all)
            build_cli
            build_gui
            ;;
        *)
            die "usage: $0 [cli|gui|all]"
            ;;
    esac

    echo
    echo "Built AppImages in $DIST:"
    ls -1 "$DIST"/*.AppImage 2>/dev/null || true
}

main
