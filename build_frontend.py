#!/usr/bin/env python3
"""
Build script to compile frontend and copy static files to Django backend
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error output: {result.stderr}")
        sys.exit(1)
    print(f"Success: {command}")
    return result.stdout

def main():
    # Get project root directory
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    backend_static_dir = project_root / "backend" / "static"
    
    print("🚀 Starting frontend build process...")
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        sys.exit(1)
    
    # Check if backend static directory exists
    if not backend_static_dir.exists():
        print("📁 Creating backend static directory...")
        backend_static_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean backend static directory
    print("🧹 Cleaning backend static directory...")
    for item in backend_static_dir.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    
    # Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    # Build frontend
    print("🔨 Building frontend...")
    run_command("npm run build", cwd=frontend_dir)
    
    # Copy static files to backend
    print("📋 Copying static files to backend...")
    frontend_out_dir = frontend_dir / "out"
    
    if not frontend_out_dir.exists():
        print("❌ Frontend build output directory not found!")
        sys.exit(1)
    
    # Copy all files from frontend/out to backend/static
    for item in frontend_out_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, backend_static_dir)
        elif item.is_dir():
            shutil.copytree(item, backend_static_dir / item.name)
    
    print("✅ Frontend build and copy process completed successfully!")
    print(f"📁 Static files are now available in: {backend_static_dir}")

if __name__ == "__main__":
    main() 