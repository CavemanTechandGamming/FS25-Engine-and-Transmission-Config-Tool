#!/usr/bin/env bash
# Install Python + Tk + build tools inside CI Linux containers.
# Usage: scripts/ci_install_linux_deps.sh <apt|dnf|pacman>
set -euo pipefail

mgr="${1:-}"
case "$mgr" in
  apt)
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y \
      ca-certificates \
      curl \
      git \
      build-essential \
      binutils \
      zip \
      python3 \
      python3-pip \
      python3-venv \
      python3-full \
      python3-dev \
      python3-tk \
      tcl \
      tk \
      tcl-dev \
      tk-dev
    ;;
  dnf)
    dnf -y install \
      ca-certificates \
      curl \
      git \
      gcc \
      gcc-c++ \
      binutils \
      zip \
      which \
      python3 \
      python3-pip \
      python3-devel \
      python3-tkinter
    ;;
  pacman)
    pacman -Syu --noconfirm
    pacman -S --noconfirm --needed \
      ca-certificates \
      curl \
      git \
      base-devel \
      binutils \
      zip \
      which \
      python \
      python-pip \
      tk
    ;;
  *)
    echo "Usage: $0 <apt|dnf|pacman>"
    exit 1
    ;;
esac

python3 --version
python3 -c "import venv, ensurepip; print('venv+ensurepip OK')"
