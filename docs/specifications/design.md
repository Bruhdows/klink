# Design

Klink starts with a marble run, but the tiles should also work for other programmable machines. Keep one smart-tile design for everything.

## First kit

- About 16-20 tiles for a Maker Faire demo.
- Automatic neighbor discovery and a Hub that works out the layout.
- Stable tile IDs, even when coordinates change.
- Identifiable modules, event handling and computer control.
- Programs that keep running after the computer is disconnected.
- Two addressable RGB LEDs on every tile.

Communication should support at least 64 tiles. Power depends on the layout and loads; 64 tiles doesn't mean unlimited motors.

## Mechanical parts

Tiles are 80 × 80 × 20 mm. Each gets twelve 6 × 3 mm magnets: eight on the sides and four on top. Use clear PETG for bases and transparent blue for tracks. Yellow accents and small white diffusers are optional. Test light transmission first; even perimeter lighting isn't required.

Bases keep the same cardinal orientation. Tracks can rotate where they fit. Electronic modules need keying so they can't connect backwards. PCB dimensions are still provisional; see [interfaces](interfaces.md).

The Hub takes two grid cells, about 160 × 80 mm and 60-80 mm tall, with six tile connections.

## Modules

Passive parts: straight and curved tracks, ramps, pillars and gates. Passive pillars don't carry power unless an interconnect is added and tested.

Electronic modules: buttons, lights, marble sensors, gates, splitters and an elevator. Use the tile's GPIO/PWM and I²C when possible. Simple modules don't need another MCU.

Test sensors with real marbles and ambient light, and check their output voltage.

MG90S servos and a 12V N20 geared motor are candidates. Measure startup/stall current and mechanical load before choosing supplies. The elevator needs its own converter, driver, end stops and stall protection. That driver belongs on the module, not every tile.

## Software

Tile firmware handles links, module ID, I/O, power switching, faults and RGB. Hub firmware handles discovery, routing limits, USB, storage and standalone programs.

The plan is a TypeScript SDK and Klink Studio in the browser. Use WebHID for Studio and CDC for SDK/development access. The SDK should work without depending on one transport.

Standalone programs should use a small event-driven format with checked actions, conditions, timers and variables. No full JavaScript runtime is needed. Storage needs safe, atomic updates and recovery. SPI flash is a candidate; capacity is undecided.

These are requirements, not finished software. Current hardware details are in [Rev A](rev-a.md).
