#include "stm32f4xx.h"
#include "tusb.h"
#ifndef KLINK_USB_VID
/* TinyUSB example identity for private bench use only; obtain an assigned
 * VID/PID before shipping. */
#define KLINK_USB_VID 0xcafe
#define KLINK_USB_PID 0x40fe
#endif
static const tusb_desc_device_t device = {.bLength = sizeof(tusb_desc_device_t),
                                          .bDescriptorType = TUSB_DESC_DEVICE,
                                          .bcdUSB = 0x0200,
                                          .bDeviceClass = TUSB_CLASS_MISC,
                                          .bDeviceSubClass =
                                              MISC_SUBCLASS_COMMON,
                                          .bDeviceProtocol = MISC_PROTOCOL_IAD,
                                          .bMaxPacketSize0 = 64,
                                          .idVendor = KLINK_USB_VID,
                                          .idProduct = KLINK_USB_PID,
                                          .bcdDevice = 0x0100,
                                          .iManufacturer = 1,
                                          .iProduct = 2,
                                          .iSerialNumber = 3,
                                          .bNumConfigurations = 1};
static const uint8_t hid_report[] = {TUD_HID_REPORT_DESC_GENERIC_INOUT(64)};
static const uint8_t config[] = {
    TUD_CONFIG_DESCRIPTOR(1, 3, 0,
                          TUD_CONFIG_DESC_LEN + TUD_CDC_DESC_LEN +
                              TUD_HID_INOUT_DESC_LEN,
                          TUSB_DESC_CONFIG_ATT_SELF_POWERED, 0),
    TUD_CDC_DESCRIPTOR(0, 4, 0x83, 8, 0x01, 0x81, 64),
    TUD_HID_INOUT_DESCRIPTOR(2, 0, HID_ITF_PROTOCOL_NONE, sizeof hid_report,
                             0x02, 0x82, 64, 5)};
const uint8_t *tud_hid_descriptor_report_cb(uint8_t itf) {
  (void)itf;
  return hid_report;
}
const uint8_t *tud_descriptor_device_cb(void) {
  return (const uint8_t *)&device;
}
const uint8_t *tud_descriptor_configuration_cb(uint8_t index) {
  (void)index;
  return config;
}
const uint16_t *tud_descriptor_string_cb(uint8_t index, uint16_t lang) {
  (void)lang;
  static uint16_t result[40];
  unsigned n = 0;
  if (index == 0) {
    result[1] = 0x0409;
    n = 1;
  } else if (index == 3) {
    static const char hex[] = "0123456789ABCDEF";
    const uint8_t *uid = (const uint8_t *)UID_BASE;
    for (unsigned i = 0; i < 12; i++) {
      result[++n] = hex[uid[i] >> 4];
      result[++n] = hex[uid[i] & 15];
    }
  } else {
    const char *s = index == 1   ? "Klink"
                    : index == 2 ? "Klink Hub bench"
                    : index == 4 ? "Control"
                                 : 0;
    if (!s)
      return 0;
    while (*s && n < 39)
      result[++n] = (uint8_t)*s++;
  }
  result[0] = (TUSB_DESC_STRING << 8) | (2 * n + 2);
  return result;
}
