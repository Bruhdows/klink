#ifndef KLINK_H
#define KLINK_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define KL_PAYLOAD 48
#define KL_FRAME 62
#define KL_PORTS 6
#define KL_BROADCAST 0xffffu
/* Wire: version,type,ttl,length,src16,dst16,seq16,payload,crc16, COBS + zero.
 */
enum {
  KL_HELLO = 1,
  KL_RGB = 2,
  KL_EVENT = 3,
  KL_GATE = 4,
  KL_STOP = 5,
  KL_FAULT = 6,
  KL_POWER = 7,
  KL_TOPOLOGY = 8,
  KL_ASSIGN = 9
};
typedef struct {
  uint8_t type, ttl, len;
  uint16_t src, dst, seq;
  uint8_t data[KL_PAYLOAD];
} kl_packet;
typedef struct {
  uint8_t data[KL_FRAME], used;
  bool discard;
} kl_decoder;
#define KL_RGB_BYTES 180
void kl_rgb_encode(const uint8_t rgb[3], uint8_t out[KL_RGB_BYTES]);
uint16_t kl_crc(const uint8_t *, size_t);
size_t kl_encode(const kl_packet *, uint8_t out[KL_FRAME]);
bool kl_feed(kl_decoder *, uint8_t, kl_packet *);
typedef void (*kl_send)(void *, uint8_t, const uint8_t *, size_t);
typedef void (*kl_deliver)(void *, const kl_packet *);
typedef struct {
  uint8_t uid[12];
  bool assigned;
  uint16_t id, seq, neighbor[KL_PORTS];
  uint32_t seen_ms[KL_PORTS];
  struct {
    uint16_t src, seq;
    uint32_t window, at;
    uint8_t uid[12];
    bool valid;
  } seen[130];
  uint32_t now;
  uint8_t ports;
  kl_decoder rx[KL_PORTS];
  kl_send send;
  kl_deliver deliver;
  void *ctx;
} kl_node;
void kl_node_init(kl_node *, uint16_t, uint8_t, kl_send, kl_deliver, void *);
void kl_receive(kl_node *, uint8_t, uint8_t, uint32_t);
void kl_publish(kl_node *, kl_packet *);
void kl_hello(kl_node *, uint32_t);
void kl_topology(kl_node *);
enum { KL_NONE, KL_BUTTON, KL_SENSOR, KL_SERVO, KL_ELEVATOR };
uint8_t kl_module(uint16_t adc12);
typedef struct {
  bool stable, candidate;
  uint32_t since;
} kl_debounce;
bool kl_debounce_step(kl_debounce *, bool, uint32_t, uint32_t);
/* A fixed-size event program, serialized independently of C struct padding. */
#define KL_RULES 16
#define KL_PROGRAM_SIZE (8 + KL_RULES * 12)
typedef struct {
  uint16_t source, target, delay_ms;
  uint8_t event, action, len, data[3];
} kl_rule;
typedef struct {
  uint8_t count;
  kl_rule rules[KL_RULES];
} kl_program;
bool kl_program_decode(kl_program *, const uint8_t *, size_t);
size_t kl_program_encode(const kl_program *, uint8_t out[KL_PROGRAM_SIZE]);
typedef struct {
  kl_program program;
  bool armed;
  struct {
    bool active;
    uint32_t due;
    kl_packet p;
  } pending[KL_RULES];
} kl_vm;
void kl_vm_stop(kl_vm *);
bool kl_vm_event(kl_vm *, const kl_packet *, uint32_t);
void kl_vm_tick(kl_vm *, kl_node *, uint32_t);
enum {
  KL_LIFT_OK = 0,
  KL_LIFT_STOP = 1,
  KL_LIFT_SUPPLY = 2,
  KL_LIFT_DRIVER = 4,
  KL_LIFT_STALE = 8,
  KL_LIFT_JAM = 16,
  KL_LIFT_CURRENT = 32
};
typedef struct {
  uint16_t fault;
  uint8_t duty;
  bool running, index;
  uint32_t command_ms, progress_ms, started_ms;
} kl_lift;
void kl_lift_init(kl_lift *);
bool kl_lift_command(kl_lift *, uint8_t, uint32_t);
uint8_t kl_lift_step(kl_lift *, uint32_t, bool, bool, bool, uint16_t, uint16_t);
bool kl_lift_clear(kl_lift *, bool, bool, uint16_t);

#define KL_SAVED_SIZE (4 + KL_PROGRAM_SIZE + 1 + 64 * 16 + 3)
typedef struct {
  uint8_t uid[12];
  uint16_t address;
  uint8_t module, rails;
} kl_identity;
typedef struct {
  uint32_t generation;
  kl_program program;
  uint8_t count;
  kl_identity identities[64];
} kl_saved;
bool kl_saved_encode(const kl_saved *, uint8_t out[KL_SAVED_SIZE]);
bool kl_saved_decode(kl_saved *, const uint8_t in[KL_SAVED_SIZE]);

#endif
