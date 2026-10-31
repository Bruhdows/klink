# Prototype plan

## Magnetic connections

Print two small connector test pieces in PETG using 6 x 3 mm magnets.

Test magnet fit, polarity, alignment and resistance to sideways movement. The connection should hold the pieces together without leaving a noticeable gap.

Once the connection works, print two full 80 x 80 x 20 mm tiles and check the fit.

## Electrical connectors

Select a spring contact and design a small PCB with matching contact pads.

Test continuity, alignment tolerance and repeated connections. The contacts must work reliably without requiring precise manual positioning.

Initial tests will use a current-limited 5V supply. Power protection and live hot-swapping will be tested separately.

## Tile communication

Use three CH32X035 development boards to test the proposed network.

Start with UART communication between two controllers, then add message forwarding through a third.

The firmware needs unique tile IDs, directional neighbor detection and automatic rediscovery when a connection changes.

The first functional test will use a button connected to one controller and an LED connected to another. The Hub should detect the connected layout and forward the button event to the correct tile.

## First PCB

Design a smart-tile PCB after the connector and communication tests.

The board will contain the CH32X035, four edge interfaces, power regulation and protection, a top module connector and programming contacts.

A small prototype batch will be used to test the complete system before producing 16 boards.

## Marble run

Develop the tracks, pillars, lift and splitter alongside the electronics.

The first mechanical test will use a simple track with an elevated section. The lift will then be added to return marbles to the upper level.

The splitter will use a servo to select between three outputs, with a sensor to detect incoming marbles.

The first complete prototype should run a continuous marble loop with software-controlled routing and automatic tile discovery.
