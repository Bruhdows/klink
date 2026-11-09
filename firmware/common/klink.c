#include "klink.h"
static uint16_t rd(const uint8_t *p) {
  return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}
static void wr(uint8_t *p, uint16_t v) {
  p[0] = (uint8_t)v;
  p[1] = (uint8_t)(v >> 8);
}
static void zero(void *p, size_t n) {
  uint8_t *b = p;
  while (n--)
    *b++ = 0;
}
uint16_t kl_crc(const uint8_t *p, size_t n) {
  uint16_t c = 0xffff;
  while (n--) {
    c ^= (uint16_t)*p++ << 8;
    for (unsigned i = 0; i < 8; i++)
      c = (uint16_t)((c << 1) ^ ((c & 0x8000) ? 0x1021 : 0));
  }
  return c;
}
size_t kl_encode(const kl_packet *p, uint8_t out[KL_FRAME]) {
  if (p->len > KL_PAYLOAD || !p->ttl)
    return 0;
  uint8_t raw[60] = {1, p->type, p->ttl, p->len};
  wr(raw + 4, p->src);
  wr(raw + 6, p->dst);
  wr(raw + 8, p->seq);
  for (unsigned i = 0; i < p->len; i++)
    raw[10 + i] = p->data[i];
  size_t n = 12 + p->len;
  wr(raw + n - 2, kl_crc(raw, n - 2));
  size_t pos = 1, codepos = 0;
  uint8_t code = 1;
  for (size_t i = 0; i < n; i++) {
    if (!raw[i]) {
      out[codepos] = code;
      codepos = pos++;
      code = 1;
    } else {
      out[pos++] = raw[i];
      code++;
    }
  }
  out[codepos] = code;
  out[pos++] = 0;
  return pos;
}
bool kl_feed(kl_decoder *d, uint8_t b, kl_packet *p) {
  if (b) {
    if (d->used >= KL_FRAME - 1)
      d->discard = true;
    else if (!d->discard)
      d->data[d->used++] = b;
    return false;
  }
  if (d->discard || !d->used) {
    d->used = 0;
    d->discard = false;
    return false;
  }
  uint8_t raw[60];
  size_t at = 0, n = 0, encoded = d->used;
  d->used = 0;
  while (at < encoded) {
    uint8_t c = d->data[at++];
    if (!c || at + c - 1 > encoded)
      return false;
    for (unsigned j = 1; j < c; j++) {
      if (n >= sizeof raw)
        return false;
      raw[n++] = d->data[at++];
    }
    if (c < 255 && at < encoded) {
      if (n >= sizeof raw)
        return false;
      raw[n++] = 0;
    }
  }
  if (n < 12 || raw[0] != 1 || !raw[2] || raw[3] > KL_PAYLOAD ||
      n != (size_t)raw[3] + 12 || rd(raw + n - 2) != kl_crc(raw, n - 2))
    return false;
  p->type = raw[1];
  p->ttl = raw[2];
  p->len = raw[3];
  p->src = rd(raw + 4);
  p->dst = rd(raw + 6);
  p->seq = rd(raw + 8);
  for (unsigned i = 0; i < p->len; i++)
    p->data[i] = raw[10 + i];
  return true;
}
void kl_node_init(kl_node *n, uint16_t id, uint8_t ports, kl_send s,
                  kl_deliver d, void *c) {
  zero(n, sizeof *n);
  n->id = id;
  n->ports = ports > KL_PORTS ? KL_PORTS : ports;
  n->send = s;
  n->deliver = d;
  n->ctx = c;
}
static bool remember(kl_node *n, const kl_packet *p) {
  if (!p->src || p->src == KL_BROADCAST)
    return false;
  unsigned free = 130;
  for (unsigned i = 0; i < 130; i++) {
    if (n->seen[i].valid && (uint32_t)(n->now - n->seen[i].at) > 4000)
      n->seen[i].valid = false;
    if (!n->seen[i].valid) {
      if (free == 130)
        free = i;
      continue;
    }
    if (n->seen[i].src != p->src)
      continue;
    bool match = true;
    for (unsigned j = 0; j < 12; j++)
      if (n->seen[i].uid[j] !=
          ((p->type == KL_TOPOLOGY && p->len == 24) ? p->data[j] : 0))
        match = false;
    if (!match)
      continue;
    int16_t delta = (int16_t)(p->seq - n->seen[i].seq);
    if (delta > 0) {
      n->seen[i].window = delta >= 32 ? 1 : (n->seen[i].window << delta) | 1;
      n->seen[i].seq = p->seq;
    } else {
      unsigned behind = (uint16_t)(-(int32_t)delta);
      if (behind >= 32 || (n->seen[i].window & (UINT32_C(1) << behind)))
        return false;
      n->seen[i].window |= UINT32_C(1) << behind;
    }
    n->seen[i].at = n->now;
    return true;
  }
  if (free == 130)
    return false; /* Fail closed when the 64-tile + Hub capacity is exceeded. */
  for (unsigned j = 0; j < 12; j++)
    n->seen[free].uid[j] =
        (p->type == KL_TOPOLOGY && p->len == 24) ? p->data[j] : 0;
  n->seen[free].src = p->src;
  n->seen[free].seq = p->seq;
  n->seen[free].window = 1;
  n->seen[free].at = n->now;
  n->seen[free].valid = true;
  return true;
}
static void flood(kl_node *n, const kl_packet *p, uint8_t except) {
  uint8_t wire[KL_FRAME];
  size_t len = kl_encode(p, wire);
  if (len && n->send)
    for (uint8_t i = 0; i < n->ports; i++)
      if (i != except)
        n->send(n->ctx, i, wire, len);
}
void kl_publish(kl_node *n, kl_packet *p) {
  p->src = n->id;
  p->seq = ++n->seq;
  if (!p->ttl)
    p->ttl = 64;
  remember(n, p);
  flood(n, p, 255);
}
void kl_receive(kl_node *n, uint8_t port, uint8_t b, uint32_t now) {
  if (port >= n->ports)
    return;
  n->now = now;
  kl_packet p;
  if (!kl_feed(&n->rx[port], b, &p))
    return;
  if (p.type == KL_HELLO && p.ttl == 1 && p.len == 12 && p.src &&
      p.src != KL_BROADCAST) {
    n->neighbor[port] = p.src;
    n->seen_ms[port] = now;
    return;
  }
  if (p.type == KL_ASSIGN && p.len == 14 && p.src == 1) {
    bool match = true;
    for (unsigned i = 0; i < 12; i++)
      if (p.data[i] != n->uid[i])
        match = false;
    uint16_t address = rd(p.data + 12);
    if (match && address >= 2 && address != KL_BROADCAST) {
      n->id = address;
      n->assigned = true;
    }
  }
  if (!remember(n, &p))
    return;
  if ((p.dst == n->id || p.dst == KL_BROADCAST) && n->deliver)
    n->deliver(n->ctx, &p);
  if (p.dst != n->id && p.ttl > 1) {
    p.ttl--;
    flood(n, &p, port);
  }
}
void kl_hello(kl_node *n, uint32_t now) {
  n->now = now;
  kl_packet p = {.type = KL_HELLO,
                 .ttl = 1,
                 .src = n->id,
                 .dst = KL_BROADCAST,
                 .seq = ++n->seq,
                 .len = 12};
  for (unsigned i = 0; i < 12; i++)
    p.data[i] = n->uid[i];
  flood(n, &p, 255);
  for (unsigned i = 0; i < n->ports; i++)
    if ((uint32_t)(now - n->seen_ms[i]) > 3000)
      n->neighbor[i] = 0;
}
void kl_topology(kl_node *n) {
  kl_packet p = {.type = KL_TOPOLOGY, .dst = 1, .ttl = 64, .len = 24};
  for (unsigned i = 0; i < 12; i++)
    p.data[i] = n->uid[i];
  for (unsigned i = 0; i < n->ports; i++)
    wr(p.data + 12 + i * 2, n->neighbor[i]);
  kl_publish(n, &p);
}
uint8_t kl_module(uint16_t a) {
  /* +/-3% of ADC full scale around nominal resistor ratios, with dead bands. */
  const uint16_t centers[] = {372, 738, 1309, 2815};
  const uint8_t types[] = {KL_BUTTON, KL_SENSOR, KL_SERVO, KL_ELEVATOR};
  for (unsigned i = 0; i < 4; i++)
    if (a + 122 >= centers[i] && a <= centers[i] + 122)
      return types[i];
  return KL_NONE;
}
bool kl_debounce_step(kl_debounce *d, bool v, uint32_t now, uint32_t delay) {
  if (v != d->candidate) {
    d->candidate = v;
    d->since = now;
  }
  if (v != d->stable && (uint32_t)(now - d->since) >= delay) {
    d->stable = v;
    return true;
  }
  return false;
}
size_t kl_program_encode(const kl_program *p, uint8_t out[KL_PROGRAM_SIZE]) {
  if (p->count > KL_RULES)
    return 0;
  zero(out, KL_PROGRAM_SIZE);
  out[0] = 'K';
  out[1] = 'L';
  out[2] = 1;
  out[3] = p->count;
  for (unsigned i = 0; i < p->count; i++) {
    const kl_rule *r = &p->rules[i];
    if (r->len > 3 ||
        (r->action != KL_RGB && r->action != KL_GATE && r->action != KL_STOP))
      return 0;
    uint8_t *b = out + 6 + i * 12;
    wr(b, r->source);
    wr(b + 2, r->target);
    wr(b + 4, r->delay_ms);
    b[6] = r->event;
    b[7] = r->action;
    b[8] = r->len;
    for (unsigned j = 0; j < 3; j++)
      b[9 + j] = r->data[j];
  }
  wr(out + KL_PROGRAM_SIZE - 2, kl_crc(out, KL_PROGRAM_SIZE - 2));
  return KL_PROGRAM_SIZE;
}
bool kl_program_decode(kl_program *p, const uint8_t *b, size_t n) {
  if (n != KL_PROGRAM_SIZE || b[0] != 'K' || b[1] != 'L' || b[2] != 1 ||
      b[3] > KL_RULES || b[4] || b[5] || rd(b + n - 2) != kl_crc(b, n - 2))
    return false;
  kl_program candidate = {.count = b[3]};
  for (unsigned i = 0; i < candidate.count; i++) {
    const uint8_t *v = b + 6 + i * 12;
    kl_rule *r = &candidate.rules[i];
    r->source = rd(v);
    r->target = rd(v + 2);
    r->delay_ms = rd(v + 4);
    r->event = v[6];
    r->action = v[7];
    r->len = v[8];
    if (r->len > 3 ||
        (r->action != KL_RGB && r->action != KL_GATE && r->action != KL_STOP))
      return false;
    if ((r->action == KL_RGB && r->len != 3) ||
        (r->action == KL_GATE && (r->len != 1 || v[9] > 1)) ||
        (r->action == KL_STOP && r->len))
      return false;
    for (unsigned j = 0; j < 3; j++)
      r->data[j] = v[9 + j];
  }
  *p = candidate;
  return true;
}
void kl_vm_stop(kl_vm *v) {
  v->armed = false;
  for (unsigned i = 0; i < KL_RULES; i++)
    v->pending[i].active = false;
}
bool kl_vm_event(kl_vm *v, const kl_packet *p, uint32_t now) {
  if (!v->armed || p->type != KL_EVENT || p->len != 1)
    return false;
  for (unsigned i = 0; i < v->program.count; i++) {
    const kl_rule *r = &v->program.rules[i];
    if ((r->source == p->src || r->source == KL_BROADCAST) &&
        r->event == p->data[0]) {
      if (v->pending[i].active) {
        kl_vm_stop(v);
        return false;
      }
      v->pending[i].active = true;
      v->pending[i].due = now + r->delay_ms;
      kl_packet *o = &v->pending[i].p;
      zero(o, sizeof *o);
      o->type = r->action;
      o->dst = r->target;
      o->ttl = 64;
      o->len = r->len;
      for (unsigned j = 0; j < r->len; j++)
        o->data[j] = r->data[j];
    }
  }
  return true;
}
void kl_vm_tick(kl_vm *v, kl_node *n, uint32_t now) {
  if (!v->armed)
    return;
  for (unsigned i = 0; i < KL_RULES; i++)
    if (v->pending[i].active && (int32_t)(now - v->pending[i].due) >= 0) {
      v->pending[i].active = false;
      kl_publish(n, &v->pending[i].p);
    }
}
void kl_lift_init(kl_lift *l) { zero(l, sizeof *l); }
bool kl_lift_command(kl_lift *l, uint8_t duty, uint32_t now) {
  if (!duty) {
    l->running = false;
    l->duty = 0;
    return true;
  }
  if (l->fault || duty > 180)
    return false;
  if (!l->running) {
    l->started_ms = now;
    l->progress_ms = now;
  }
  l->command_ms = now;
  l->duty = duty;
  l->running = true;
  return true;
}
uint8_t kl_lift_step(kl_lift *l, uint32_t now, bool stop_closed, bool driver_ok,
                     bool index, uint16_t ma, uint16_t mv) {
  if (!stop_closed)
    l->fault |= KL_LIFT_STOP;
  if (!driver_ok)
    l->fault |= KL_LIFT_DRIVER;
  if (mv < 10000 || mv > 13200)
    l->fault |= KL_LIFT_SUPPLY;
  if (index != l->index) {
    l->index = index;
    l->progress_ms = now;
  }
  if (l->running) {
    if ((uint32_t)(now - l->command_ms) > 500)
      l->fault |= KL_LIFT_STALE;
    if ((uint32_t)(now - l->progress_ms) > 1500)
      l->fault |= KL_LIFT_JAM;
    if (ma > 400)
      l->fault |= KL_LIFT_CURRENT;
  }
  if (l->fault) {
    l->running = false;
    l->duty = 0;
  }
  return l->running ? l->duty : 0;
}
bool kl_lift_clear(kl_lift *l, bool stop_closed, bool driver_ok, uint16_t mv) {
  if (l->running || !stop_closed || !driver_ok || mv < 10000 || mv > 13200)
    return false;
  kl_lift_init(l);
  return true;
}
bool kl_saved_encode(const kl_saved *s, uint8_t out[KL_SAVED_SIZE]) {
  if (s->count > 64)
    return false;
  zero(out, KL_SAVED_SIZE);
  for (unsigned i = 0; i < 4; i++)
    out[i] = s->generation >> (8 * i);
  if (!kl_program_encode(&s->program, out + 4))
    return false;
  out[4 + KL_PROGRAM_SIZE] = s->count;
  for (unsigned i = 0; i < s->count; i++) {
    uint8_t *p = out + 5 + KL_PROGRAM_SIZE + i * 16;
    for (unsigned j = 0; j < 12; j++)
      p[j] = s->identities[i].uid[j];
    wr(p + 12, s->identities[i].address);
    p[14] = s->identities[i].module;
    p[15] = s->identities[i].rails;
  }
  wr(out + KL_SAVED_SIZE - 3, kl_crc(out, KL_SAVED_SIZE - 3));
  out[KL_SAVED_SIZE - 1] = 0xff;
  return true;
}
bool kl_saved_decode(kl_saved *s, const uint8_t in[KL_SAVED_SIZE]) {
  if (in[KL_SAVED_SIZE - 1] ||
      rd(in + KL_SAVED_SIZE - 3) != kl_crc(in, KL_SAVED_SIZE - 3) ||
      in[4 + KL_PROGRAM_SIZE] > 64)
    return false;
  kl_saved candidate = {0};
  if (!kl_program_decode(&candidate.program, in + 4, KL_PROGRAM_SIZE))
    return false;
  for (unsigned i = 0; i < 4; i++)
    candidate.generation |= (uint32_t)in[i] << (8 * i);
  candidate.count = in[4 + KL_PROGRAM_SIZE];
  for (unsigned i = 0; i < candidate.count; i++) {
    const uint8_t *p = in + 5 + KL_PROGRAM_SIZE + i * 16;
    kl_identity *id = &candidate.identities[i];
    id->address = rd(p + 12);
    id->module = p[14];
    id->rails = p[15];
    if (id->rails > 3 || id->module > KL_ELEVATOR ||
        (id->rails && id->module == KL_NONE) ||
        (id->rails & 2 && id->module != KL_ELEVATOR))
      return false;
    if (id->address < 2 || id->address == KL_BROADCAST)
      return false;
    for (unsigned j = 0; j < 12; j++)
      id->uid[j] = p[j];
    for (unsigned j = 0; j < i; j++) {
      bool same = true;
      for (unsigned k = 0; k < 12; k++)
        if (candidate.identities[j].uid[k] != id->uid[k])
          same = false;
      if (same || candidate.identities[j].address == id->address)
        return false;
    }
  }
  *s = candidate;
  return true;
}
/* WS2812B V5: 24MHz SPI, 30 ticks/bit = 1.25us. Zero: 8 high / 22 low;
 * one: 15 high / 15 low. Nominal widths: 333/917ns and 625/625ns.
 * Both LEDs share RGB. The wire is GRB, MSB first. */
void kl_rgb_encode(const uint8_t rgb[3], uint8_t out[KL_RGB_BYTES]) {
  unsigned at = 0, used = 0;
  zero(out, KL_RGB_BYTES);
  for (unsigned led = 0; led < 2; led++)
    for (unsigned channel = 0; channel < 3; channel++) {
      uint8_t value = rgb[channel == 0 ? 1 : channel == 1 ? 0 : 2];
      for (int bit = 7; bit >= 0; bit--) {
        uint32_t code = value & (1u << bit) ? (0x7fffUL << 15) : (0xffUL << 22);
        unsigned count = 30;
        while (count) {
          unsigned take = 8 - used;
          if (take > count)
            take = count;
          out[at] = (uint8_t)((out[at] << take) |
                              ((code >> (count - take)) & ((1u << take) - 1)));
          used += take;
          count -= take;
          if (used == 8) {
            at++;
            used = 0;
          }
        }
      }
    }
}
