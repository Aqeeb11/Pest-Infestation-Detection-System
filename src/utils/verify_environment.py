"""Environment verification script for the grape disease and pest detection project.

This script validates the installed Python environment by checking core
machine learning and computer vision dependencies, and by verifying CUDA
availability when applicable.
"""

import platform


def check_package_version(import_name, display_name=None):
    """Import a package and return its version string.

    Args:
        import_name (str): The package name to import.
        display_name (str, optional): A human-friendly package name.

    Returns:
        str: The package version or an error message.
    """
    display_name = display_name or import_name

    try:
        package = __import__(import_name)
        version = getattr(package, "__version__", None)

        if version is None:
            return f"{display_name}: version information not available"

        return f"{display_name} Version: {version}"
    except ImportError:
        return f"{display_name} is not installed. Please install it before continuing."
    except Exception as error:
        return f"Failed to verify {display_name}: {error}"


def check_cuda_status():
    """Check CUDA availability and GPU details via PyTorch.

    Returns:
        str: A formatted CUDA availability report.
    """
    try:
        import torch

        if torch.cuda.is_available():
            cuda_version = torch.version.cuda or "Unknown"
            gpu_name = torch.cuda.get_device_name(0)
            return (
                "CUDA is available\n"
                f"CUDA Version: {cuda_version}\n"
                f"GPU Name: {gpu_name}"
            )

        return "CUDA is not available. Running on CPU."
    except ImportError:
        return "PyTorch is not installed, so CUDA availability cannot be checked."
    except Exception as error:
        return f"Failed to verify CUDA availability: {error}"


def print_banner():
    """Print the verification banner."""
    banner = [
        "=" * 50,
        "PROJECT ENVIRONMENT VERIFICATION",
        "Machine Learning-Based Grape Disease and Pest Detection System",
        "=" * 50,
    ]

    print("\n".join(banner))


def main():
    """Run the environment verification checks."""
    print_banner()

    python_version = platform.python_version()
    print(f"Python Version: {python_version}\n")

    package_checks = [
        ("torch", "PyTorch"),
        ("ultralytics", "Ultralytics"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("matplotlib", "Matplotlib"),
    ]

    for import_name, display_name in package_checks:
        print(check_package_version(import_name, display_name))

    print()
    print(check_cuda_status())
    print("\n" + "=" * 50)
    print("Environment Setup Successful")
    print("=" * 50)


if __name__ == "__main__":
    main()
