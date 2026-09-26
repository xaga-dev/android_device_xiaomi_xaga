#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'hardware/mediatek',
    'hardware/mediatek/libion_mtk',
    'hardware/xiaomi',
    'vendor/xiaomi/mt6895-common',
]

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
}


_displayservice_ping = (
    b'_ZN7lineage10frameworks14displayservice4V1_014IEventCallback4pingEv'
)
_displayservice_unresolved = (
    rb'_ZN7lineage10frameworks14displayservice4V1_01[45]I[A-Za-z0-9_]*'
    rb'(?:linkToDeath|unlinkToDeath|getDebugInfo|getHashChain|'
    rb'interfaceChain|interfaceDescriptor|5debug|registerForNotifications)'
    rb'[A-Za-z0-9_]*'
)
_displayservice_ctor_vtable = (
    rb'_ZTCN[A-Za-z0-9_]+E\d+_'
    rb'N7lineage10frameworks14displayservice4V1_01[45]I[A-Za-z0-9_]*E'
)


blob_fixups: blob_fixups_user_type = {
    'vendor/etc/sensors/hals.conf': blob_fixup()
        .regex_replace('android.hardware.sensors@2.X-subhal-mediatek.so', 'android.hardware.sensors@2.0-subhal-impl-1.0.so')
        .regex_replace('sensors.touch.detect.so', 'sensors.dynamic_sensor_hal.so'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/etc/libnfc-nxp.conf': blob_fixup()
        .regex_replace('(NXPLOG_.*_LOGLEVEL)=0x03', '\\1=0x02')
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    'vendor/lib64/hw/audio.primary.mediatek.so': blob_fixup()
        .replace_needed('libstagefright_foundation.so', 'libstagefright_foundation-v33.so')
        .replace_needed('libalsautils.so', 'libalsautils-v31.so')
        .replace_needed('libtinyxml2.so', 'libtinyxml2-v34.so')
        .binary_regex_replace(b'A2dpsuspendonly', b'A2dpSuspended\x00\x00')
        .binary_regex_replace(b'BTAudiosuspend', b'A2dpSuspended\x00'),
    ('vendor/lib64/mt6895/libmtkcam_stdutils.so', 'vendor/lib64/hw/mt6895/android.hardware.camera.provider@2.6-impl-mediatek.so'): blob_fixup()
        .replace_needed('libutils.so', 'libutils-v32.so'),
    ('vendor/lib64/mt6895/libcam.hal3a.so', 'vendor/lib64/mt6895/libcam.hal3a.ctrl.so', 'vendor/lib64/mt6895/libmtkcam_request_requlator.so'): blob_fixup()
        .add_needed('libprocessgroup_shim.so'),
    'vendor/lib64/libalhLDC.so': blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    ('vendor/lib64/lib3a.ae.pipe.so', 'vendor/lib64/mt6895/libaaa_toneutil.so', 'vendor/lib64/mt6895/lib3a.flash.so', 'vendor/lib64/mt6895/lib3a.sensors.color.so', 'vendor/lib64/mt6895/lib3a.sensors.flicker.so'): blob_fixup()
        .add_needed('liblog.so'),
    'vendor/lib64/mt6895/libmtkcam_hal_android_app_cbadaptor.so': blob_fixup()
        .replace_needed('android.frameworks.displayservice@1.0.so',
                        'lineage.frameworks.displayservice@1.0.so')
        .binary_regex_replace(
            b'7android10frameworks14displayservice',
            b'7lineage10frameworks14displayservice')
        .binary_regex_replace(
            _displayservice_unresolved,
            lambda m: _displayservice_ping.ljust(len(m.group(0)), b'\x00'))
        .binary_regex_replace(
            _displayservice_ctor_vtable,
            lambda m: _displayservice_ping.ljust(len(m.group(0)), b'\x00')),
}  # fmt: skip

module = ExtractUtilsModule(
    'xaga',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'mt6895-common', module.vendor
    )
    utils.run()
