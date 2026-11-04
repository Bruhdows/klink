# BOM

The [tile BOM CSV](../../hardware/electronics/tile/bom.csv) has all 130 references, quantities, footprints and purchase links. It's a working list, not an assembly order. Blank prices mean unknown, not free.

The target is 35-45 PLN per assembled tile. There isn't a quote confirming that yet.

## Parts in the schematic

These have datasheet checks behind them, but still need sample and assembly tests. Prices and stock aren't confirmed.

- U1: CH32X035G8U6. 1 per tile, 20 for 20 tiles. [LCSC C7437027](https://www.lcsc.com/product-detail/C7437027.html).
- U2: AP2112K-3.3TRG1. 1 per tile, 20 for 20 tiles. [LCSC C51118](https://www.lcsc.com/product-detail/C51118.html).
- U3: TPS259470LRPWR. 1 per tile, 20 for 20 tiles. [LCSC C3662793](https://www.lcsc.com/product-detail/C3662793.html).
- U4: LMR36520ADDAR. 1 per tile, 20 for 20 tiles. [TI order page](https://www.ti.com/product/LMR36520/part-details/LMR36520ADDAR).
- U5, U7: TPS26600PWPR. 2 per tile, 40 for 20 tiles. [TI order page](https://www.ti.com/product/TPS2660/part-details/TPS26600PWPR).
- U6: SN74AHCT1G125DBVR. 1 per tile, 20 for 20 tiles. [TI order page](https://www.ti.com/product/SN74AHCT1G125/part-details/SN74AHCT1G125DBVR).
- U8-U11: SN74LVC2G125DCUR. 4 per tile, 80 for 20 tiles. [TI order page](https://www.ti.com/product/SN74LVC2G125/part-details/SN74LVC2G125DCUR).
- U12, U13: TMUX1511PWR. 2 per tile, 40 for 20 tiles. [TI order page](https://www.ti.com/product/TMUX1511/part-details/TMUX1511PWR).
- U14: TPS3808G01DBVR. 1 per tile, 20 for 20 tiles. [TI order page](https://www.ti.com/product/TPS3808/part-details/TPS3808G01DBVR).
- U15: SN74LVC1G08DBVR. 1 per tile, 20 for 20 tiles. [TI order page](https://www.ti.com/product/SN74LVC1G08/part-details/SN74LVC1G08DBVR).
- D1, D3: WS2812B-V5. 2 per tile, 40 for 20 tiles. [LCSC C2846931](https://www.lcsc.com/product-detail/C2846931.html).
- D4, D5: SMBJ22CA-E3/52, Vishay. 2 per tile, 40 for 20 tiles. [Vishay part data](https://www.vishay.com/docs/88392/smbj.pdf), distributor quote pending.
- D6, D7: SMBJ22A-E3/52, Vishay. 2 per tile, 40 for 20 tiles. Same family, distributor quote pending.
- F1-F5: 0466001.NR, Littelfuse. 5 per tile, 100 for 20 tiles. [LCSC C151134](https://www.lcsc.com/product-detail/C151134.html).
- L1: SRP7050TA-150M, Bourns. 1 per tile, 20 for 20 tiles. [Distributor listing](https://www.digikey.com/en/products/detail/bourns-inc/SRP7050TA-150M/5429680).
- C7: 6TPE120MAZB, Panasonic. 1 per tile, 20 for 20 tiles. [Distributor listing](https://www.digikey.com/en/products/detail/panasonic-industry/6TPE120MAZB/4146639).

The old AP63205/AP2171 pricing no longer applies. [Rev A](rev-a.md) has the circuit limits and datasheet links.

## Connectors

SAMZO 03E315320 is the preferred sample. The plan uses two spring bodies and two flat mating faces per tile: 40 connectors for twenty tiles, or 50 with spares. [LCSC C42402947](https://www.lcsc.com/product-detail/C42402947.html).

On 2026-11-02 the cached listing showed 90 in stock and USD 0.4748 each at 30+. That's about USD 18.99 for 40 or USD 23.74 for 50, before tax, shipping and assembly. The listing was four months old. Get a fresh quote. Current-rating conditions, stroke, force, plating and land width still need confirmation.

Alternatives kept for comparison:

- [Harwin S1961-46R](https://www.digikey.de/en/products/detail/harwin-inc/S1961-46R/14558804): ten contacts per tile, 200 for twenty. Cached pricing was EUR 0.32150 at 100+, or EUR 64.30 for 200; listed stock was 9,347. Carrier boards, finish and holding force add to the cost.
- SAMZO [23E315050](https://www.lcsc.com/product-detail/C42402977.html) and [23E415050](https://www.lcsc.com/product-detail/C42402981.html): two of each per tile if used. Mating/current details and imported pad numbering aren't settled. The 2026-11-01 cached estimate for 23E415050 was USD 0.3604 at 30+.
- [Xinyangze C7471693](https://www.lcsc.com/product-detail/C7471693.html): module-side pogo candidate. Cached USD 0.5163 at 10+, about USD 5.16 for ten pins. Listed as 30V/2A, 5.2mm working height, 6.9mm overall and 50mΩ. Manufacturer details and samples still need checking.

These are estimates in different currencies, not landed costs or current stock confirmations. [Interfaces](interfaces.md) covers fit and plating. Put spring pins on modules, not eight on every tile.

## Still to buy or select

J3-J7 have no released footprints. J1 and test points are bare copper; J2 is DNP and excluded from the PCB. They have no purchased-component quantity.

Exact ceramic capacitor and resistor parts are unfinished. Check voltage, power, tolerance, ripple and DC-bias loss. UART resistors need 2.2k, 1%, at least 0.25W in 1206. C7 and the fuses have temperature limits in [Rev A](rev-a.md).

Twenty tiles need 240 magnets: 160 side and 80 top, all 6 × 3 mm. PETG mass, fasteners and module counts still need measuring. The marble target is 16mm glass.

The repeated costs add up: MCUs, converters, protection, fuses, buffers, LEDs and possibly four carrier PCBs per tile. Keep one universal base and simple module electronics. Don't remove protection to hit the price target. MG90S servos and a 12V N20 motor are still candidates; loads aren't measured. TB6612FNG isn't a selected 20V input stage.

Quote electronics, PCB/assembly, stencil/setup, hand work, PETG/magnets, modules, Hub, supply and cable separately. Include extended-part fees, shipping and taxes. Price the 3-5 board trial batch separately. Mark owned parts as owned.

## Hub input and repeated costs

The [Hub BOM](../../hardware/electronics/hub/bom.csv) is exported from the implemented input, six outputs and common shutdown. It contains seven TPS26630, seven INA301A1IDGKR, seven CSD19537Q3 and seven BSS138LT1G devices, plus control logic and seven rail clamps. The open-drain fault groups use two triple Schmitt AND packages, avoiding a separate buffer for every fault flag. It excludes the future MCU, main regulators, USB data and storage. Blank MPN fields remain purchase selections. Copper test points have no purchased-component cost. C9 is now a selected 10µF/50V 1206 part; effective capacitance and assembly remain qualification items.

For one prototype, allow roughly USD 65–105 additional parts for the six output circuits and shared shutdown, before PCB, assembly, tax and shipping. This uses small-quantity price bands, not a complete supplier quote. Reference DigiKey prices checked on 2026-11-03 were [TPS26630RGER](https://www.digikey.com/en/products/detail/texas-instruments/TPS26630RGER/10820326) USD 5.13 at one or 3.907 at ten, [INA301A1IDGKR](https://www.digikey.com/en/products/detail/texas-instruments/INA301A1IDGKR/6571979) 3.45 or 2.592, and [CSD19537Q3](https://www.digikey.com/en/products/detail/texas-instruments/CSD19537Q3/5438037) 2.13 or 1.356. Precision resistors, the specified C0G ramp capacitors, remaining small parts and logic are allowances. This range includes their prototype-quantity premiums. The independent precision trips and shared latch are retained; they are not repeated on twenty tiles.

TPS26630 sourcing is a risk. TI and the checked large distributors showed no RGER stock. [LCSC's RGET listing](https://www.lcsc.com/product-image/C2864391.html) showed eight units in a cached result, USD 3.6238 each. RGET is an approved reel-size alternate in the BOM, not a different circuit. Recheck stock and authenticity before ordering; seven devices are needed for one Hub, leaving little sample margin. Do not substitute TPS26631/32 variants without rechecking their pulse-current and OVP behavior.

The repeated tile cost drivers remain 40 TPS26600 devices, 20 TPS259470L switches, 20 LMR36520 converters, 80 UART buffers, 40 analog switches and 100 fuses. The recommended transit-fuse change would remove 80 fuse placements in a future qualified revision; F1 and local protection remain. No such change has been applied to the current tile BOM. Contacts, carrier joints and finish must first support the aggregate current and hot resistance targets in [Rev A](rev-a.md).

Doubling spring bodies on the two sprung faces would add forty bodies across twenty tiles, roughly USD 19 at the old cached connector price, plus assembly and wider carriers. That is about USD 0.95/tile before those costs. It does not establish equal sharing or reduce the required rating after one contact opens. Start with a small sample batch and obtain compression, force, plating, resistance and 5A test conditions before selecting the production arrangement. Neither board is ready for production fabrication.
