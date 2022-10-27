cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project($project_name C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable($project_name
  main.c
)

# enable std output to usb comport
pico_enable_stdio_usb($project_name $enable_usb_stdio)

# disable std output to uart
pico_enable_stdio_uart($project_name $enable_uart_stdio)

pico_add_extra_outputs($project_name)

target_link_libraries($project_name pico_stdlib)
