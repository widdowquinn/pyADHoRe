# README.md - patch

This directory contains the fiel `osx_iadhore.patch`, a patch to the `i-ADHoRe` 3.0.01 package necessary for compilation on OSX Mavericks and Yosemite. This patch specifies use of the `libstdc++` library, and replaces all instances of `uint` in the source with `unsigned int`. This allows the package to be compiled with Apple's command-line tools.

To use the patch, copy the file to the directory above the downloaded source (so if your source is in the `i-adhore-3.0.01` directory, copy the file to the parent of that directory). Then issue:

```
patch -p0 -i mavericks.patch
```

You should see the output:

```
patching file i-adhore-3.0.01/CMakeLists.txt
patching file i-adhore-3.0.01/src/BaseCluster.h
patching file i-adhore-3.0.01/src/GHM.h
patching file i-adhore-3.0.01/src/SynthenicCloud.cpp
patching file i-adhore-3.0.01/src/SynthenicCloud.h
patching file i-adhore-3.0.01/src/bmp/color.cpp
patching file i-adhore-3.0.01/src/bmp/pnghandling.cpp
patching file i-adhore-3.0.01/src/bmp/pnghandling.h
```