cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(test_project C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(main
  main.c
)

# enable std output to usb comport
pico_enable_stdio_usb(main 1)

# disable std output to uart
pico_enable_stdio_uart(main 0)

pico_add_extra_outputs(main)

target_link_libraries(main pico_stdlib)
