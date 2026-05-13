cmake_minimum_required(VERSION 3.22.1)
project(harphymnal_synth)

# Oboe ships as a Gradle prefab dependency — the AGP toolchain exposes
# it via find_package() once `implementation 'com.google.oboe:oboe:…'`
# is declared in app/build.gradle.
find_package(oboe REQUIRED CONFIG)

add_library(harphymnal_synth SHARED oboe_synth.cpp)

target_link_libraries(harphymnal_synth
    PRIVATE
        oboe::oboe
        android
        log)
