"""Installation file for the ansys-api-mechanical package"""

import os
from datetime import datetime

import setuptools

from ansys.tools.protoc_helper import BuildPyCommand, DevelopCommand

# Get the long description from the README file
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

product = "mechanical"
library = ""
package_info = ["ansys", "api", product, library, "v0"]
with open(os.path.join(HERE, "src", "ansys", "api", product, library, "VERSION"), encoding="utf-8") as f:
    version = f.read().strip()

package_name = "ansys-api-mechanical"
dot_package_name = '.'.join(filter(None, package_info))

description = f"Autogenerated python gRPC interface package for {package_name}, built on {datetime.now().strftime('%H:%M:%S on %d %B %Y')}"


class build_py(BuildPyCommand):
    def build_package_data(self) -> None:
        self.data_files = [
            (
                package,
                src_dir,
                build_dir,
                [f for f in filenames if not f.endswith(".proto")],
            )
            for package, src_dir, build_dir, filenames in self.data_files
        ]
        return super().build_package_data()


if __name__ == "__main__":
    setuptools.setup(
        name=package_name,
        version=version,
        author="ANSYS, Inc.",
        author_email='support@ansys.com',
        description=description,
        long_description=long_description,
        long_description_content_type='text/markdown',
        url=f"https://github.com/ansys/{package_name}",
        license="MIT",
        python_requires=">=3.7",
        install_requires=["grpcio~=1.30", "protobuf>=3.19,<6"],
        package_dir = {"": "src"},
        packages=setuptools.find_namespace_packages("src", include=("ansys.*",)),
        package_data={
            "": ["*.proto", "*.pyi", "py.typed", "VERSION"],
        },
        entry_points={
            "ansys.tools.protoc_helper.proto_provider": [
                f"{dot_package_name}={dot_package_name}"
            ],
        },
        cmdclass={"build_py": build_py, "develop": DevelopCommand},
    )
