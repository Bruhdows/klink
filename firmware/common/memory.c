#include <stddef.h>
void *memcpy(void *d, const void *s, size_t n) {
  unsigned char *a = d;
  const unsigned char *b = s;
  while (n--)
    *a++ = *b++;
  return d;
}
void *memset(void *d, int v, size_t n) {
  unsigned char *a = d;
  while (n--)
    *a++ = (unsigned char)v;
  return d;
}
void __aeabi_memcpy(void *d, const void *s, size_t n) { memcpy(d, s, n); }
void __aeabi_memcpy4(void *d, const void *s, size_t n) { memcpy(d, s, n); }
void __aeabi_memclr4(void *d, size_t n) { memset(d, 0, n); }
void *memmove(void *d, const void *s, size_t n) {
  unsigned char *a = d;
  const unsigned char *b = s;
  if (a < b)
    while (n--)
      *a++ = *b++;
  else {
    a += n;
    b += n;
    while (n--)
      *--a = *--b;
  }
  return d;
}
int memcmp(const void *a, const void *b, size_t n) {
  const unsigned char *x = a, *y = b;
  while (n--) {
    if (*x != *y)
      return *x - *y;
    x++;
    y++;
  }
  return 0;
}
size_t strlen(const char *s) {
  size_t n = 0;
  while (s[n])
    n++;
  return n;
}
void __aeabi_memclr(void *d, size_t n) { memset(d, 0, n); }
