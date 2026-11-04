# Klink

Klink is a magnetic tile system for building programmable machines. First up: a marble run with sensors, buttons, lights, gates, splitters and an elevator.

The plan is a 16-20 tile kit for Maker Faire. Each tile is 80 × 80 × 20 mm, with four neighbor connections and two RGB LEDs. A Hub will handle USB, layout discovery and programs that run without a computer.

Rev A uses a 20V bus, with 5V and 3.3V made on each tile. The schematic is in place, but the connectors and protection still need testing. The PCB isn't routed. Disconnect power before moving tiles.

- [Design](docs/specifications/design.md)
- [Electronics](docs/specifications/rev-a.md)
- [Connectors and pinouts](docs/specifications/interfaces.md)
- [BOM](docs/specifications/BOM.md)
- [Next steps](docs/specifications/prototype-plan.md)

Hardware sources are in `hardware/electronics/` and `hardware/cad/`. Firmware, SDK and Studio are still planned work.
