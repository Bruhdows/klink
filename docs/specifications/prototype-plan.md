# Next steps

## Samples and fit

The committed straight-track STL is older than the SCAD. Export from the current source before printing.

Order magnets and SAMZO 03E315320 samples. Confirm the missing dimensions and working compression, then print the [connector fixture](interfaces.md#fit-tests). Check alignment, continuity, magnet polarity, holding force, sideways slip and repeated mating. Try lifting the center out with four neighbors held down.

Test the top interface with offset, tilt and reversed insertion. Nothing should let 20V touch a signal pad. Keep these tests unpowered.

## Power and communication

Finish the Hub's branch protection and total cutoff. Check faults through grid loops, not just a chain. Test the buck on a current-limited supply, then both module outputs with electronic loads. Measure ripple, startup, temperature and short-circuit recovery before adding motors.

Use three CH32X035 boards for discovery and forwarding. Then run four UARTs, RGB and hardware I²C together. Test brownout, missing neighbors, duplicate packets and stuck-bus recovery. Check the actual MCU silicon lot supports I²C.

## First boards

Low-voltage placement can continue. Connector fit and power protection need to be settled before high-voltage placement and routing.

After the [release checks](validation.md#before-ordering), order 3-5 trial boards. Test those before making the rest. Another revision might still be needed.

Then finish the Hub and start with button/light modules, followed by sensors, servos and the elevator. Measure motor and servo stall loads first.

The demo should run a marble loop, react to events, identify tiles with RGB and keep running without a laptop. Rearrange tiles only with power disconnected.
