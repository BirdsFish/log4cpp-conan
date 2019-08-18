import os

from conans import ConanFile
from conans.tools import download, untargz, patch
from conans import CMake


class Log4cppConan(ConanFile):
    name = "log4cpp"
    version = "1.1.3"
    description = "A library of C++ classes for flexible logging to files (rolling), syslog, IDSA and other destinations. It is modeled after the Log for Java library (http://www.log4j.org), staying as close to their API as is reasonable."
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    url="https://sourceforge.net/projects/log4cpp/"
    license="https://sourceforge.net/p/log4cpp/codegit/ci/master/tree/COPYING"
    exports = ["CMakeLists.txt", "include/*"]

    def source(self):
        patch_content="""
--- include/log4cpp/config-MinGW32.h	2019-08-18 23:39:33.112548160 +0200
+++ include/log4cpp/config-MinGW32.h	2019-08-18 23:41:15.188766397 +0200
@@ -24,7 +24,7 @@
 /* define if the compiler has int64_t */
 #ifndef LOG4CPP_HAVE_INT64_T
 #define LOG4CPP_HAVE_INT64_T
-#define int64_t __int64
+// #define int64_t __int64

 /* define if the compiler has in_addr_t */
 #ifndef LOG4CPP_HAVE_IN_ADDR_T

--- CMakeLists.txt	2019-08-18 23:39:33.120548178 +0200
+++ CMakeLists.txt	2019-08-18 23:45:26.413243877 +0200
@@ -82,7 +82,9 @@

 IF (WIN32)
   TARGET_LINK_LIBRARIES (${LOG4CPP_LIBRARY_NAME} kernel32 user32 ws2_32 advapi32 )
-  SET_TARGET_PROPERTIES(${LOG4CPP_LIBRARY_NAME} PROPERTIES LINK_FLAGS /NODEFAULTLIB:msvcrt )
+  IF (MSVC)
+    SET_TARGET_PROPERTIES(${LOG4CPP_LIBRARY_NAME} PROPERTIES LINK_FLAGS /NODEFAULTLIB:msvcrt )
+  ENDIF (MSVC)
 ENDIF (WIN32)

 INSTALL (
@@ -97,4 +97,5 @@
 INSTALL (
   TARGETS ${LOG4CPP_LIBRARY_NAME}
   ARCHIVE DESTINATION lib
+  LIBRARY DESTINATION lib
   )
 """

        zip_name = "log4cpp-%s.tar.gz" % self.version
        url = "https://sourceforge.net/projects/log4cpp/files/latest/download"
        download(url, zip_name)
        untargz(zip_name)
        os.system("cp -R log4cpp/* .") # hack to build as dependency
        os.unlink(zip_name)
        patch(patch_string=patch_content)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="*", dst="include", src="include", keep_path=True)

        # Copying static and dynamic libs
        self.copy(pattern="*.a", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=".", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=".", keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=".", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['log4cpp']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
