# Parts research

Current component candidates for Klink. The initial target is 16 intelligent tiles. Prices, availability and datasheets need to be checked before ordering.

## Microcontrollers

- [CH32X035G8U6](https://www.lcsc.com/product-detail/C7437027.html) - Current choice. Four UART peripherals, 62 KB flash and 20 KB RAM.
- [CH32V005F6P6](https://www.lcsc.com/product-detail/C54824605.html) - Cheaper alternative with two UARTs.

The CH32X035 should allow independent communication on all four tile edges. The pin assignments still need verification, especially with the module interface.

## Connectors

- [G-Switch C22463675](https://www.lcsc.com/product-detail/C22463675.html) - 4-pin spring connector.
- [SAMZO C42402943](https://www.lcsc.com/product-detail/C42402943.html) - 5-pin spring connector.
- [SAMZO C42402982](https://www.lcsc.com/product-detail/C42402982.html) - 6-pin right-angle contact. Mating geometry unverified.

The proposed design uses spring contacts on the north and east edges, with matching PCB pads on the south and west edges.

Each tile would need two spring connectors, giving 32 connectors for 16 tiles. A 4 x 4 grid has 24 connections between tiles.

The final connector needs to fit within the tile walls, support repeated connections and provide enough contacts for power and communication.

## Power

- [SY6280AAAC](https://www.lcsc.com/product-detail/C207620.html) - Candidate 5V current-limited power switch.
- [AP2112K-3.3](https://www.lcsc.com/product-detail/C51118.html) - 3.3V regulator.
- External regulated power supply for the Hub.
- Additional protection components to be selected during schematic design.

The current plan is to distribute 5V between tiles, with local 3.3V regulation. Power routing, backfeeding and hot-swapping still need to be addressed.

Motors will require appropriately rated power connections.

## Mechanical

- 6 x 3 mm neodymium magnets, approximately 128 for 16 tiles, plus spares.
- PETG for tiles and modules.
- 16 mm glass marbles.
- Screws and threaded inserts for mounting electronics.

## Modules

- MG90S servo for the splitter.
- N20 geared motor for the lift.
- TB6612FNG motor driver, depending on motor requirements.
- IR emitters and receivers for marble detection.
- WS2812B RGB LEDs.
- Tactile buttons.

Motor selection depends on the final lift mechanism.

## Development

- WCH-LinkE programmer.
- Three compatible microcontroller development boards.
- Breadboard, jumper wires and basic components.
- Multimeter and current-limited power supply.

Custom PCBs will likely be ordered through JLCPCB. The first batch should contain only a few boards to test the design before ordering all 16.
