# BOM

The root [bom.csv](../../bom.csv) is the consolidated purchasing and funding worksheet. It covers sixteen tiles, one Hub, one elevator, button/sensor/gate electronics, contacts, magnets, fabrication, assembly, mechanics, power supply, cables and delivered-cost allowances. Per-board CSVs retain engineering references and selected MPNs. Bare copper pads are not purchased components. `budget_class` separates the base estimate, owned material and the explicit uncertainty row; the latter is not a purchase SKU.

## Current estimate

At 2026-11-09, the sixteen-tile worksheet totals USD 1,372.89 before a separate 25% uncertainty allowance of USD 343.22, or USD 1,716.11 including it. This is a provisional engineering budget, not a supplier quote or an approved funding request. 121 of the 137 purchase rows still use explicitly marked engineering allowances. Several material links still identify a supplier/category rather than a selected purchasable SKU. Close those rows before submitting a purchase-linked final BOM.

The separate three-tile electronics trial estimate is USD 897.29 plus USD 224.32 uncertainty. The five-tile trial estimate is USD 961.87 plus USD 240.47 uncertainty. These include the Hub, elevator, electronic-module bring-up, power/cabling, contact fixtures and small-batch overhead. They exclude the full return's baseboard/rods/foot fasteners. Minimum bare-board batches and component order multiples are counted. Reuse successful trial assemblies in the final sixteen; do not add the two project totals together.

Owned PETG has zero requested purchase cost. Three kilograms is a material reservation, not a weighed stock or slicer result. Existing tools and unpaid assembly time have no grant charge. Confirm available plastic before slicing the final kit.

The earlier 35-45 PLN assembled-tile target has no supporting quote. The worksheet preserves the sixteen-tile kit and all protection. It does not achieve that target by reducing the tile count.

## Checked sourcing

Electronic supplier pages were read on 2026-11-08 and rechecked where noted on 2026-11-09. Electronic prices exclude assembly, shipping and tax and do not reserve stock. The local magnet comparison below includes listed Polish VAT and domestic delivery.

- [TPS26600PWPR, C544399](https://www.lcsc.com/product-image/C544399.html): USD 1.0992 at 30+, 6,387 shown. The kit needs 33 across tiles and Hub. The 32 tile devices cost USD 35.17 at that tier, USD 93.47 below the earlier USD 4.02 each allowance. The circuit is unchanged.
- [LMR36520ADDAR, C2879422](https://www.lcsc.com/product-image/C2879422.html): USD 1.0022 at 10+, 5,727 shown; seventeen required.
- [CH32X035G8U6, C7437027](https://www.lcsc.com/product-image/C7437027.html): USD 0.4234 at 10+, 8,785 shown; sixteen required.
- [TMUX1511PWR, C2866750](https://www.lcsc.com/product-image/C2866750.html): USD 0.3304 at 30+, 7,205 shown; thirty-five required.
- [TPS259470LRPWR, C3662793](https://www.lcsc.com/product-image/C3662793.html), checked 2026-11-09: USD 0.9211 at 10+, USD 1.021 at 1+, with 1,333 shown on the image-page listing. This replaces the earlier four-piece snapshot. The product-detail response did not expose live stock; confirm sixteen plus assembler attrition and JLC inventory before ordering. The MPN and circuit are unchanged.
- [TPS26630RGET, C2864391](https://www.lcsc.com/product-image/C2864391.html): out of stock. The old USD 3.0921 LCSC price does not settle availability. The current worksheet instead budgets seven approved RGET cut-tape parts at [DigiKey's USD 4.81 reference price](https://www.digikey.com/en/products/detail/texas-instruments/TPS26630RGET/10434724), or USD 33.67. Stock is zero; the displayed 250 expected on 2026-11-19 is not a delivery commitment. Buying ten at USD 3.659 would cost USD 36.59, so the smaller unit-price tier would increase the basket. RGET remains the approved reel-size alternate to RGER; do not substitute a different TPS2663 variant. The public [TI RGET page](https://www.ti.com/product/TPS2663/part-details/TPS26630RGET) and [Mouser RGER page](https://www.mouser.com/en/ProductDetail/Texas-Instruments/TPS26630RGER?qs=vLWxofP3U2ztcw332RlqMw%3D%3D), checked on 2026-11-09, also show no available stock. No authorized deliverable source is confirmed.
- [0466001.NR](https://www.mouser.com/en/ProductDetail/Littelfuse/0466001.NR?qs=ar9f0rk5DXDy6tpNfF8WnQ%3D%3D): retain eighty 1A fuses. LCSC C151134 is unavailable; the checked Mouser cut-tape listing shows USD 0.555 at 50+. No full reel or MouseReel is needed.

The worksheet also records checked tiers and unavoidable order multiples for AP2112, SN74LVC244A, the AHCT RGB buffer, the LVC AND gate and both selected 10k resistor types. Their MPNs are retained. Similar-looking marketplace substitutes are not approved.

## Cost changes checked on 2026-11-09

The base estimate falls by USD 71.20 from USD 1,444.09. This is a change in the purchasing estimate, not a saving on an order already placed. No supplier has quoted the complete kit.

- Magnets: the USD 113.40 allowance becomes USD 33.82 including listed domestic delivery. Hunter's published 10+ tier is PLN 0.45 gross. For 268 pieces, PLN 120.60 plus PLN 11.99 delivery is PLN 132.59. Convert using [NBP table 218/A/2026](https://static.nbp.pl/dane/kursy/xml/a218z261109.xml), 2026-11-09, USD/PLN 3.9199. This reduces the line by USD 79.58. The page has inconsistent headline prices; use the published quantity table conservatively and confirm the basket. Buying 300 at PLN 0.43 would cost PLN 129 before delivery, more than 268 at PLN 0.45. Do not buy extra magnets just to reach that tier.
- Tile TPS259470L: sixteen at the displayed USD 0.9211 tier cost USD 14.74, USD 4.00 below the earlier reference. Confirm current stock and assembly sourcing; LCSC stock is not JLC inventory.
- Hub TPS26630: using the approved RGET cut-tape alternate raises the seven-device estimate from USD 21.64 to USD 33.67, a USD 12.03 increase. It remains unavailable for immediate shipment.
- Five SAMZO wear bodies: the one-piece tier is USD 0.6701, making USD 3.35 instead of the USD 3.00 allowance. [The checked listing](https://www.lcsc.com/product-image/C42402947.html?whichImg=0) shows only 25 bodies against 35 production plus five wear samples. Do not count the unavailable 30+ tier as a kit saving. Production bodies retain their allowance.

The USD 170 tile assembly, USD 150 Hub fabrication/assembly, USD 140 electronics freight/import/VAT reserve, USD 65 elevator fabrication/assembly and USD 45.50 edge-carrier rows remain unquoted. Magnet domestic freight and VAT are already in the magnet line. No carrier-elimination, free shipping, assembly-classification or tax-recovery saving is included. The 25% uncertainty is a budget allowance, not a statistical confidence interval.

## Assembly plan

All six boards place purchased components on the front side. The tile has 109 populated purchase positions, 41 selected MPNs and 349 numbered solder joints before unreleased contacts. The Hub has 309 purchased board positions and 68 MPNs; its other schematic references are bare test copper. Off-board optical parts remain separate purchased items.

[JLCPCB's current capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) allow Economic PCBA on single-sided 2/4/6-layer boards, with a standard stackup, 0.4mm minimum IC pitch and limited finish options. The tile's 0.4mm MCU pitch meets that listed minimum. Economic eligibility is not confirmed: the 0.10mm MCU ground fanout, selected parts, stencil, finish and the full order still need supplier review. Edge plating, castellations and gold fingers are not supported by that service. Do not quietly choose those processes to eliminate carriers while budgeting Economic PCBA.

The checked [assembly fee schedule](https://jlcpcb.com/help/article/pcb-assembly-price) lists USD 8.18 Economic setup, USD 1.53 stencil, USD 0.0016 per SMT joint and USD 3.07 per ordinary extended feeder. If all 41 tile MPNs incurred that feeder fee, loading alone would be USD 125.87 per order. Actual Basic/Preferred classification can lower it. Tile SMT joints calculate to USD 1.68/2.79/8.93 for 3/5/16 boards, before feeders, X-ray, manual joints, PCB fabrication and tax. Confirm every footprint rotation against the assembly preview. Avoid a second assembly side and speculative spare component purchases.

Do not order main boards until routing and connector/protection release. A single 16-board batch fits the listed Economic order-volume range of 2-50 boards and avoids repeated setup and feeder loading. It does not establish stock or complete-order eligibility. At the published rates, avoiding a second tile order saves one USD 8.18 setup plus USD 1.53 stencil and any repeated extended feeders, subject to the actual quotation. Keep the USD 170 allowance until the complete BOM, X-ray, attrition, board finish and assembly preview are priced. Buy only the trial population before electrical qualification. Obtain a quote for the minimum Hub/elevator population rather than assuming one-board Economic assembly is available. The BOM service rows are allowances for this unresolved choice. Hand-assemble the small service modules with owned tools where practical.

## Mechanical quantities

The current contact budget retains seventy edge carriers: sixty-four tile faces and six Hub faces. Thirty-five faces are sprung in the fixed cardinal arrangement. Five separate SAMZO bodies and eight top-contact candidates are budgeted for qualification; worn specimens are not production inventory. Side contacts remain sample candidates; no carrier-removal savings are counted. Four electronic modules need thirty-two top contacts; passive tracks need none.

Magnets total 268: 192 in sixteen bases, twelve Hub side magnets and sixty-four across the removable modules. The current procurement candidate is [Magnesy Hunter MAGN_17#4_W/6x3](https://magnesyhunter.pl/pl/p/Magnes-neodymowy-6x3-mm-N45-walcowy/175), EAN 5906728444490: nominal 6x3mm, axial N45 and NiCuNi. This retains the previous candidate's grade and finish. Piece sales remove the old ten-piece order multiple. Confirm dimensional tolerances, retention, adhesive and printed fit on samples before accepting the full quantity. No magnet-to-tile holding-force test has passed.

The [M6 cut list](../../hardware/manufacturing/rod-cut-list.csv) fits eighteen rods into five one-metre bars. It includes 2mm saw kerf per cut and 4mm end trim per bar. Its 4,068mm finished length assumes a 12mm baseboard and 8mm below-board nut/washer/thread allowance. Measure actual material and nut stacks before cutting. The [54-hole drilling list](../../hardware/manufacturing/baseboard-drill.csv) uses the same support stations. Thirty supported track seats plus eighteen clamped rod anchors require ninety-six M6 nut/washer pairs; thirty-six M4x25 sets attach the nine feet.

PCB mount choices are ordinary M2 nuts and screws, avoiding inserts. Tile screws are M2x8; the elevated Hub PCB uses M2x30 and a nominal 0.6mm washer stack. Elevator screws are M2x10 and gate service-board screws M2x6. Printed nut pockets assume 4.0mm across flats and at most 1.6mm thickness, with clearance. Print fit and screw engagement remain tests. The gate uses two M2x30 clamp screws and an M3 axle; supplied servo horn hardware still needs checking.

Retain [Pololu 3044](https://www.pololu.com/product/3044), the 12V 250:1 HPCB gearmotor, at the checked USD 26.45 listing. An unspecified local N20 cannot be adopted without ratio, winding/current, shaft, body and torque data. The selected gate prototype uses [FEETECH FS90](https://www.pololu.com/product/2818), listed at USD 8.40 and documented for 3.3V control, avoiding an additional level-shifter board. Servo clamp/horn fit and stall current remain untested.

## Earlier selection evidence

The material below records previous part selections and historical allowances. Current quantities, procurement status and project totals are in the root CSV above. Do not add these older cost ranges to the current total.

## Parts in the schematic

These have datasheet checks behind them, but still need sample and assembly tests. Prices and stock aren't confirmed.

- U1: CH32X035G8U6. 1 per tile, 20 for 20 tiles. [LCSC C7437027](https://www.lcsc.com/product-detail/C7437027.html).
- U2: AP2112K-3.3TRG1. 1 per tile, 20 for 20 tiles. [LCSC C51118](https://www.lcsc.com/product-detail/C51118.html).
- U3: TPS259470LRPWR. 1 per tile, 20 for 20 tiles. [LCSC C3662793](https://www.lcsc.com/product-detail/C3662793.html).
- U4: LMR36520ADDAR. 1 per tile, 20 for 20 tiles. [TI order page](https://www.ti.com/product/LMR36520/part-details/LMR36520ADDAR).
- U5, U7: TPS26600PWPR. 2 per tile, 40 for 20 tiles. [TI order page](https://www.ti.com/product/TPS2660/part-details/TPS26600PWPR).
- U6: SN74AHCT1G125DBVR. 1 per tile, 20 for 20 tiles. [TI order page](https://www.ti.com/product/SN74AHCT1G125/part-details/SN74AHCT1G125DBVR).
- U8: SN74LVC244APWR. 1 per tile, 20 for 20 tiles. [TI order page](https://www.ti.com/product/SN74LVC244A/part-details/SN74LVC244APWR).
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

Exact ceramic capacitor and resistor selections are present in the current CSVs. Check stock, voltage, power, tolerance, ripple and effective capacitance against those MPNs. UART resistors use 2.2k, 1%, at least 0.25W in 1206. C7 and the fuses have temperature limits in [Rev A](rev-a.md). J3-J7 still lack released purchase parts; bare test/debug copper and the excluded factory connector are not missing purchase selections.

Twenty tiles need 240 magnets: 160 side and 80 top, all 6 × 3 mm. PETG mass, fasteners and module counts still need measuring. The marble target is 16mm glass.

The repeated costs add up: MCUs, converters, protection, fuses, buffers, LEDs and possibly four carrier PCBs per tile. Keep one universal base and simple module electronics. Don't remove protection to hit the price target. MG90S servos and a 12V N20 motor are still candidates; loads aren't measured. TB6612FNG isn't a selected 20V input stage.

Quote electronics, PCB/assembly, stencil/setup, hand work, PETG/magnets, modules, Hub, supply and cable separately. Include extended-part fees, shipping and taxes. Price the 3-5 board trial batch separately. Mark owned parts as owned.

## Hub input and repeated costs

The [Hub BOM](../../hardware/electronics/hub/bom.csv) is exported from the full 350-component schematic, including input protection, six outputs, supplies, MCU, USB, UART interfaces, storage and diagnostics. It contains seven TPS26630, seven INA301A1IDGKR, seven CSD19537Q3 and seven BSS138LT1G devices, plus control logic and seven rail clamps. The open-drain fault groups use two triple Schmitt AND packages, avoiding a separate buffer for every fault flag. The full Hub still needs PCB layout and electrical qualification; its USB and execution firmware is not implemented. Blank MPN fields remain purchase selections. Copper test points have no purchased-component cost. C9 is now a selected 10µF/50V 1206 part; effective capacitance and assembly remain qualification items.

For one prototype, allow roughly USD 65–105 additional parts for the six output circuits and shared shutdown, before PCB, assembly, tax and shipping. This uses small-quantity price bands, not a complete supplier quote. Reference DigiKey prices checked on 2026-11-03 were [TPS26630RGER](https://www.digikey.com/en/products/detail/texas-instruments/TPS26630RGER/10820326) USD 5.13 at one or 3.907 at ten, [INA301A1IDGKR](https://www.digikey.com/en/products/detail/texas-instruments/INA301A1IDGKR/6571979) 3.45 or 2.592, and [CSD19537Q3](https://www.digikey.com/en/products/detail/texas-instruments/CSD19537Q3/5438037) 2.13 or 1.356. Precision resistors, the specified C0G ramp capacitors, remaining small parts and logic are allowances. This range includes their prototype-quantity premiums. The independent precision trips and shared latch are retained; they are not repeated on twenty tiles.

TPS26630 sourcing is a risk. TI and the checked large distributors showed no RGER stock. [LCSC's RGET listing](https://www.lcsc.com/product-image/C2864391.html) showed eight units in a cached result, USD 3.6238 each. RGET is an approved reel-size alternate in the BOM, not a different circuit. Recheck stock and authenticity before ordering; seven devices are needed for one Hub, leaving little sample margin. Do not substitute TPS26631/32 variants without rechecking their pulse-current and OVP behavior.

The repeated tile cost drivers remain 40 TPS26600 devices, 20 TPS259470L switches, 20 LMR36520 converters, 20 octal UART buffers, 40 analog switches and 100 fuses. V1 retains the original 1A transit fuses. Do not budget removal of the sixty-four transit placements in a sixteen-tile kit. F1 and local protection remain unchanged. Contacts, carrier joints and finish must first support the aggregate current and hot resistance targets in [Rev A](rev-a.md).

Doubling spring bodies on the two sprung faces would add forty bodies across twenty tiles, roughly USD 19 at the old cached connector price, plus assembly and wider carriers. That is about USD 0.95/tile before those costs. It does not establish equal sharing or reduce the required rating after one contact opens. Start with a small sample batch and obtain compression, force, plating, resistance and 5A test conditions before selecting the production arrangement. Neither board is ready for production fabrication.

## Assembly selections

The tile CSV now includes quantities for 16 and 32 tiles alongside the existing 20-tile column. Standard electronic parts have manufacturer selections; J3-J7 remain unreleased connectors. Bare copper test/debug pads do not represent purchased parts. Procurement links, live stock and prices still need a consolidated quote. Capacitor effective values and package clearances must be qualified before ordering assembled boards.

UART consolidation removes three buffer packages and three bypass capacitors per tile, plus four packages and four capacitors at the Hub. That removes 104 placements from a sixteen-tile kit. Parts savings are `4 × dual-buffer price - octal-buffer price + 3 × bypass price` per tile. Illustrative USD 0.15/0.25/0.01 prices give about USD 0.38/tile plus assembly savings; these are assumptions, not quotes. Essential power and module protection is retained.

Allow approximately USD 100–150 for the full Hub's prototype parts, excluding PCB/assembly, with the earlier six-output protection allowance included rather than added twice. The tile allowance remains provisional. Carrier fabrication, attachment and finish require quotes; lower realistic loads remove the present justification for doubling spring bodies.

The [elevator BOM](../../hardware/electronics/elevator/bom.csv) covers its 47 board positions. Order one [Pololu 3044](https://www.pololu.com/product/3044) motor and one [TCST2103](https://www.vishay.com/docs/81147/tcst2103.pdf) separately, plus the normally closed stop and mechanical transmission after fit review. Reserve roughly USD 10–20 for prototype electronics and USD 26.45 for the motor at the manufacturer listing checked on 2026-11-06, before PCB, mechanics, shipping and tax. These are not a finished supplier quote.


The printed elevator prototype adds thirty M2×16 hinge screws with nuts, an [SKF 623-2Z bearing](https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/623-2z) (3×10×4mm), an M3 idler axle and ordinary frame/clamp screws. It needs no additional motor or gearbox. Final fastener lengths, bearing retention, optical-sensor mounting and the module harness need a dry assembly before a production quote.

Using the existing allowances, sixteen tiles are USD 448–864. Including the Hub parts allowance, elevator electronics and the checked motor price gives about USD 584–1060 before Hub/elevator PCB assembly, magnets, plastic, other modules, shipping and tax. This is not a supplier quote. The universal tile, sixteen-tile minimum, continuous elevator and controllable gate/splitter remain V1 scope.

Two declared 3D references remain unavailable: the tile's WQFN-28 4×4mm package and the Hub's Abracon ASE 3.2×2.5mm oscillator. Eight other footprint types have no declared model. No substitute geometry was added. Full component/enclosure collision review remains incomplete.


Hub R1 now specifies RC2512FK-7W470RL: 470Ω, 1%, 2W at 70°C, 6.35×3.10mm body. The previous 0805 purchase number did not match its 2512 footprint or 2W requirement. The resistance and circuit are unchanged. The [Yageo part sheet](https://www.yageogroup.com/component-documentation/download/specsheet/RC2512FK-7W470RL) confirms the selection; stock and board-temperature derating still need procurement/assembly review.

The seven CSD19537Q3 positions now use a local land pattern correcting the stock source/gate pad centers to 0.650mm pitch. The previous centers left 0.140mm gaps. The corrected 0.150mm gaps follow [TI SLPS549B section 7.2](https://www.ti.com/lit/ds/symlink/csd19537q3.pdf). Drain copper and the stencil now follow sections 7.2 and 7.3 as well: 0.450×0.310mm source/gate paste apertures, 0.450×0.340mm drain-finger apertures, and two 1.445×1.020mm drain-body apertures. Land and stencil assembly qualification still needs the supplier. The purchase part and electrical pin mapping are unchanged.

## Bench modules and kit costs

The [button BOM](../../hardware/electronics/button/bom.csv) and [sensor BOM](../../hardware/electronics/marble-sensor/bom.csv) cover the new service-header prototypes. The sensor's TSAL6200 and TEFT4300 are wired off-board. Its 220Ω emitter resistor is RC1206FR-07220RL, 0.25W in 1206, to retain dissipation margin if the emitter is shorted. Neither board releases the spring-contact interface or proves marble detection.

Retain USD 584–1060 for sixteen tile assemblies, Hub parts, elevator electronics and the motor, with the exclusions above; gate/splitter parts are also unquoted. Add USD 5–13 as a parts allowance for one button and one sensor, before their PCB fabrication and assembly. The printable return and elevator add roughly a kilogram or more of solid-volume PETG; slicer infill, supports, guards and guides change the actual mass. Budget plastic by sliced mass and keep machine time separate. Rods, nuts, fasteners, the baseboard, mating harnesses, top spring contacts and module magnets need a separate quote. The mating harness purchase parts and final frame fastener lengths remain unselected. These are allowances, not a production price.

The [S-06-03-N sample candidate](https://www.supermagnete.pl/eng/disc-magnets-neodymium/disc-magnet-6mm-3mm_S-06-03-N) specifies 6×3mm, ±0.1mm, axial N45 and Ni-Cu-Ni plating. The checked listing gives EUR 0.37 each in a ten-piece pack, including VAT, before shipping. Thirty samples cost EUR 11.10. Its steel pull-force listing does not establish retention between printed tiles. The sixteen bases alone need 192 magnets; Hub and module magnets are additional.

Before final Hub routing, quote three assembly alternatives. R412-R415 can use one isolated four-resistor 10k/1% array while retaining all four nets; this removes three placements if the array, footprint and placement quote justify it. [Yageo's YC/TC data](https://www.yageogroup.com/component-documentation/download/specsheet/YC164-FR-071KL) provides the relevant family data; no array substitution is selected yet. Quote production debug access with Hub J2 PD_SERVICE and J4 SWD unpopulated, using a test fixture while retaining copper access. Finally, compare qualified direct side contacts with the 64 carrier boards and their attachment operations in a sixteen-tile kit. Do not count any of these savings yet. Keep the per-port enable pull-downs, precision trips, independent shutdown and transit fuses.

The elevator vias now sit outside solder lands. The tile MCU ground via has moved out of its solder land; the localized 0.10mm ground fanout and 0.125mm clearance still need assembler acceptance. Include that requirement, stackup and stencil review in the fabrication quote.
