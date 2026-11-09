#include "klink.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned delivered, sent;
static void tx(void *c, uint8_t p, const uint8_t *d, size_t n) {
  (void)c;
  (void)p;
  (void)d;
  assert(n > 0 && n <= KL_FRAME);
  sent++;
}
static void rx(void *c, const kl_packet *p) {
  (void)c;
  (void)p;
  delivered++;
}
static void inject(kl_node *n, unsigned port, kl_packet *p, uint32_t now) {
  uint8_t b[KL_FRAME];
  size_t len = kl_encode(p, b);
  assert(len);
  for (size_t i = 0; i < len; i++)
    kl_receive(n, port, b[i], now);
}
static void framing(void) {
  assert(kl_crc((const uint8_t *)"123456789", 9) == 0x29b1);
  for (unsigned length = 0; length <= KL_PAYLOAD; length++)
    for (unsigned byte = 0; byte < 256; byte++) {
      kl_packet p = {.type = KL_RGB,
                     .ttl = 64,
                     .src = 2,
                     .dst = 1,
                     .seq = 65535,
                     .len = length},
                q;
      for (unsigned i = 0; i < length; i++)
        p.data[i] = (uint8_t)(byte + i);
      uint8_t b[KL_FRAME];
      size_t n = kl_encode(&p, b);
      assert(n && n <= KL_FRAME);
      kl_decoder d = {0};
      for (size_t i = 0; i < n - 1; i++)
        assert(!kl_feed(&d, b[i], &q));
      assert(kl_feed(&d, b[n - 1], &q));
      assert(q.src == p.src && q.seq == p.seq && q.len == length &&
             !memcmp(p.data, q.data, length));
      b[n / 2] ^= 1;
      bool good = false;
      for (size_t i = 0; i < n; i++)
        good |= kl_feed(&d, b[i], &q);
      assert(!good);
    }
  kl_decoder d = {0};
  kl_packet q;
  for (unsigned i = 0; i < 200; i++)
    assert(!kl_feed(&d, 1, &q));
  assert(!kl_feed(&d, 0, &q));
  assert(!d.used && !d.discard);
}
static void routing(void) {
  kl_node n;
  kl_node_init(&n, 4, 4, tx, rx, 0);
  kl_packet p = {.type = KL_EVENT,
                 .ttl = 3,
                 .src = 8,
                 .dst = KL_BROADCAST,
                 .seq = 2,
                 .len = 1};
  delivered = sent = 0;
  inject(&n, 0, &p, 1);
  assert(delivered == 1 && sent == 3);
  inject(&n, 1, &p, 2);
  assert(delivered == 1 && sent == 3);
  p.seq++;
  p.dst = 4;
  inject(&n, 0, &p, 3);
  assert(delivered == 2 && sent == 3);
  p.seq++;
  p.dst = 5;
  p.ttl = 1;
  inject(&n, 0, &p, 4);
  assert(delivered == 2 && sent == 3);
  p.type = KL_EVENT;
  p.dst = KL_BROADCAST;
  p.ttl = 2;
  p.seq = 10;
  p.src = 8;
  inject(&n, 0, &p, 20);
  unsigned old = delivered;
  for (unsigned i = 10; i < 60; i++) {
    p.src = i;
    inject(&n, 0, &p, 21);
  }
  assert(delivered == old + 50);
  p.src = 8;
  inject(&n, 1, &p, 22);
  assert(delivered == old + 50);
  p.type = KL_HELLO;
  p.src = 8;
  p.ttl = 1;
  p.len = 12;
  inject(&n, 2, &p, 100);
  assert(n.neighbor[2] == 8);
  kl_hello(&n, 3201);
  assert(!n.neighbor[2]);
}
static void programs(void) {
  kl_program p = {.count = 1,
                  .rules = {{.source = 3,
                             .target = 4,
                             .delay_ms = 20,
                             .event = 1,
                             .action = KL_GATE,
                             .len = 1,
                             .data = {1}}}},
             q;
  uint8_t b[KL_PROGRAM_SIZE];
  assert(kl_program_encode(&p, b) == sizeof b);
  assert(kl_program_decode(&q, b, sizeof b) && q.rules[0].target == 4);
  b[16] ^= 1;
  assert(!kl_program_decode(&q, b, sizeof b));
  kl_vm vm = {.program = p, .armed = true};
  kl_node n;
  kl_node_init(&n, 1, 6, tx, rx, 0);
  kl_packet event = {.type = KL_EVENT, .src = 3, .len = 1, .data = {1}};
  sent = 0;
  assert(kl_vm_event(&vm, &event, 0xfffffff0));
  kl_vm_tick(&vm, &n, 3);
  assert(!sent);
  kl_vm_tick(&vm, &n, 4);
  assert(sent == 6);
  assert(kl_vm_event(&vm, &event, 10));
  assert(!kl_vm_event(&vm, &event, 11) && !vm.armed);
  kl_vm_tick(&vm, &n, 100);
  assert(sent == 6);
}
static void persistence(void) {
  kl_saved saved = {.generation = 0xffffffff, .count = 2};
  saved.identities[0].address = 3;
  saved.identities[1].address = 4;
  saved.identities[1].uid[0] = 1;
  uint8_t b[KL_SAVED_SIZE];
  kl_saved decoded;
  assert(kl_saved_encode(&saved, b));
  assert(!kl_saved_decode(&decoded, b));
  b[sizeof b - 1] = 0;
  assert(kl_saved_decode(&decoded, b) && decoded.generation == 0xffffffff &&
         decoded.identities[1].address == 4);
  for (unsigned i = 0; i < sizeof b; i++) {
    b[i] ^= 1;
    assert(!kl_saved_decode(&decoded, b));
    b[i] ^= 1;
  }
  saved.identities[1].address = 3;
  assert(kl_saved_encode(&saved, b));
  b[sizeof b - 1] = 0;
  assert(!kl_saved_decode(&decoded, b));
}
static void lift(void) {
  kl_lift l;
  kl_lift_init(&l);
  assert(!kl_lift_step(&l, 0, true, true, 0, 0, 12000));
  assert(kl_lift_command(&l, 100, 1));
  assert(kl_lift_step(&l, 500, true, true, 0, 300, 12000) == 100);
  assert(!kl_lift_step(&l, 502, true, true, 0, 300, 12000) &&
         (l.fault & KL_LIFT_STALE));
  assert(!kl_lift_command(&l, 100, 503));
  assert(!kl_lift_clear(&l, false, true, 12000));
  assert(kl_lift_clear(&l, true, true, 12000));
  assert(kl_lift_command(&l, 100, 0));
  for (unsigned i = 100; i < 1500; i += 100) {
    assert(kl_lift_command(&l, 100, i));
    assert(kl_lift_step(&l, i, true, true, 0, 300, 12000));
  }
  assert(kl_lift_command(&l, 100, 1501));
  assert(!kl_lift_step(&l, 1501, true, true, 0, 300, 12000) &&
         (l.fault & KL_LIFT_JAM));
  for (unsigned f = 0; f < 4; f++) {
    kl_lift_init(&l);
    assert(kl_lift_command(&l, 100, 0));
    assert(!kl_lift_step(&l, 5, f != 0, f != 1, 0, f == 2 ? 401 : 0,
                         f == 3 ? 14000 : 12000));
    assert(l.fault);
  }
  assert(!kl_lift_command(&l, 181, 6));
}
static void led_waveform(void) {
  uint8_t rgb[3] = {0xa5, 0x3c, 0x81}, wire[KL_RGB_BYTES];
  kl_rgb_encode(rgb, wire);
  for (unsigned led = 0; led < 2; led++)
    for (unsigned c = 0; c < 3; c++)
      for (unsigned bit = 0; bit < 8; bit++) {
        unsigned n = (led * 24 + c * 8 + bit) * 30, high = 0;
        bool low = false;
        for (unsigned t = 0; t < 30; t++) {
          bool one = (wire[(n + t) / 8] >> (7 - (n + t) % 8)) & 1;
          if (one) {
            assert(!low);
            high++;
          } else
            low = true;
        }
        bool expected = (rgb[c == 0 ? 1 : c == 1 ? 0 : 2] >> (7 - bit)) & 1;
        assert(high == (expected ? 15u : 8u));
        double h = high / 24.0, l = (30 - high) / 24.0;
        assert(h >= (expected ? .580 : .220) && h <= (expected ? 1.0 : .380));
        assert(l >= .580 && l <= 1.0);
      }
}
int main(void) {
  led_waveform();
  framing();
  routing();
  programs();
  persistence();
  lift();
  assert(kl_module(372) == KL_BUTTON && kl_module(738) == KL_SENSOR &&
         kl_module(2815) == KL_ELEVATOR);
  assert(kl_module(0) == KL_NONE && kl_module(4095) == KL_NONE);
  puts("framing, routing, program integrity, wraparound, overload and lift "
       "safety passed");
}
