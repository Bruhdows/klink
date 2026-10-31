# Klink design

Klink is a modular building system with magnetic tiles and programmable components. The first application is a marble run with a motorized lift, sensors and three-way splitters.

## Tiles

The base tiles are 80 x 80 x 20 mm and will be printed in PETG. Each tile contains a small PCB, with magnets and electrical contacts along its edges.

The current connector concept uses spring contacts against PCB pads. Magnets hold neighboring tiles together, while recessed alignment features keep the contacts in place. The exact connector geometry still needs testing.

Tiles will also support vertical construction through pillars that carry power and data between levels.

The initial target is 16 intelligent tiles.

## Electronics

The current microcontroller candidate is the CH32X035G8U6. It has four UART peripherals, potentially allowing a separate serial connection on each side of the tile. Pin assignments still need verification.

Each tile communicates with its neighbors and forwards messages through the network. A central Hub connects the board to a computer over USB-C.

The planned power system uses a protected 5V supply with local 3.3V regulation. Higher-current modules, such as the lift, will require a separate power connection.

Power distribution, hot-swapping and connections that create network loops still need to be worked out.

## Modules

Modules attach to the top of a tile. The proposed interface uses I2C for communication and a method for identifying the attached module.

Initial modules include marble tracks, ramps, pillars, a motorized lift, a three-way splitter, marble sensors, buttons and RGB lights.

The module interface should also support custom hardware.

## Software

Each tile has a unique ID and reports its neighbors to the Hub. The Hub uses this information to reconstruct the board layout and expose connected modules to the desktop application.

Modules can be addressed by their position or ID. Events and commands travel through the tile network.

Example API:

```js
const button = board.at(0, 1).module();
const light = board.at(2, 1).module();

button.on("pressed", () => {
    light.setColor("#ff0000");
});
```

Marble run example:

```js
const lift = board.at(3, 0).module();
const splitter = board.at(1, 2).module();

await lift.start();

splitter.on("marble_detected", async () => {
    await splitter.setRoute("left");
});
```

These examples describe the intended API. Neither is implemented yet.

The firmware will need neighbor discovery, message routing and reconnection handling. The first version may require a fixed tile orientation to simplify layout detection.

## Current status

The mechanical design is in the early prototype stage. The tile dimensions and magnet arrangement are provisional.

The CH32X035 is the leading MCU candidate, but no PCB schematic has been finalized. Spring contacts, module connections and power protection still need physical testing.

The next prototype will focus on magnetic alignment, electrical contacts and communication between three microcontrollers.
