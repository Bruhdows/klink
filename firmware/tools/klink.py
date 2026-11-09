#!/usr/bin/env python3
"""POSIX USB CDC commissioning client. Python standard library only."""
import argparse
import binascii
import json
import os
import select
import struct
import termios
import time

PAYLOAD = 48
PROGRAM_SIZE = 200
ACTIONS = {"rgb": 2, "gate": 4, "stop": 5}
MODULES = {"button": 1, "sensor": 2, "servo": 3, "elevator": 4}


def crc(data):
    return binascii.crc_hqx(data, 0xffff)


def encode(kind, data=b"", destination=1, sequence=0):
    if len(data) > PAYLOAD or not 0 <= destination <= 65535:
        raise ValueError("invalid packet size/address")
    raw = struct.pack("<BBBBHHH", 1, kind, 64, len(data), 1, destination, sequence)
    raw += data
    raw += struct.pack("<H", crc(raw))
    wire = bytearray([0])
    code_position, code = 0, 1
    for byte in raw:
        if byte:
            wire.append(byte)
            code += 1
        else:
            wire[code_position] = code
            code_position = len(wire)
            wire.append(0)
            code = 1
    wire[code_position] = code
    return bytes(wire) + b"\0"


def decode(wire):
    if not wire or len(wire) > 61 or 0 in wire:
        raise ValueError("invalid COBS frame")
    raw = bytearray()
    at = 0
    while at < len(wire):
        code = wire[at]
        at += 1
        if at + code - 1 > len(wire):
            raise ValueError("truncated COBS frame")
        raw += wire[at:at + code - 1]
        at += code - 1
        if code < 255 and at < len(wire):
            raw.append(0)
    if len(raw) < 12 or raw[0] != 1 or not raw[2] or raw[3] > PAYLOAD:
        raise ValueError("invalid packet header")
    if len(raw) != raw[3] + 12 or crc(raw[:-2]) != struct.unpack("<H", raw[-2:])[0]:
        raise ValueError("invalid packet length/CRC")
    _, kind, ttl, _, source, destination, sequence = struct.unpack("<BBBBHHH", raw[:10])
    return {"type": kind, "ttl": ttl, "source": source, "destination": destination,
            "sequence": sequence, "data": bytes(raw[10:-2])}


def program(document):
    rules = document["rules"]
    if len(rules) > 16:
        raise ValueError("at most 16 rules")
    image = bytearray(PROGRAM_SIZE)
    image[:4] = bytes([ord("K"), ord("L"), 1, len(rules)])
    for index, rule in enumerate(rules):
        kind = ACTIONS[rule["action"]]
        data = bytes(rule.get("data", []))
        if ((kind == 2 and len(data) != 3) or
                (kind == 4 and (len(data) != 1 or data[0] > 1)) or
                (kind == 5 and data)):
            raise ValueError("invalid rule action payload")
        struct.pack_into("<HHHBBB3s", image, 6 + 12 * index,
                         rule["source"], rule["target"], rule.get("delay_ms", 0),
                         rule["event"], kind, len(data), data)
    struct.pack_into("<H", image, PROGRAM_SIZE - 2, crc(image[:-2]))
    return bytes(image)


class Connection:
    def __init__(self, port):
        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        attributes = termios.tcgetattr(self.fd)
        attributes[0] = attributes[1] = attributes[3] = 0
        attributes[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attributes[4] = attributes[5] = termios.B115200
        attributes[6][termios.VMIN] = attributes[6][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, attributes)
        self.sequence = 0
        self.buffer = bytearray()

    def close(self):
        os.close(self.fd)

    def send(self, kind, data=b"", destination=1):
        self.sequence = (self.sequence + 1) & 65535
        remaining = memoryview(encode(kind, data, destination, self.sequence))
        deadline = time.monotonic() + 2
        while remaining:
            if time.monotonic() > deadline:
                raise TimeoutError("USB write timed out")
            if select.select([], [self.fd], [], .1)[1]:
                try:
                    remaining = remaining[os.write(self.fd, remaining):]
                except BlockingIOError:
                    pass

    def packets(self, duration):
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            if not select.select([self.fd], [], [], min(.1, max(0, deadline - time.monotonic())))[0]:
                continue
            chunk = os.read(self.fd, 512)
            if not chunk:
                continue
            self.buffer += chunk
            while 0 in self.buffer:
                stop = self.buffer.index(0)
                frame = bytes(self.buffer[:stop])
                del self.buffer[:stop + 1]
                if not frame:
                    continue
                try:
                    yield decode(frame)
                except ValueError:
                    continue
            if len(self.buffer) > 61:
                # Keep a discard marker until the next delimiter, matching the MCU decoder.
                self.buffer[:] = b"\xff" * 62

    def request(self, kind, data=b"", destination=1):
        self.send(kind, data, destination)
        for packet in self.packets(3):
            if (packet["type"] == 6 and packet["source"] == 1 and
                    packet["sequence"] == self.sequence and len(packet["data"]) == 2):
                fault, storage = packet["data"]
                if fault:
                    raise RuntimeError("Hub fault latched; inspect hardware/status, then controlled restart")
                return storage
        raise TimeoutError("Hub did not acknowledge command")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("discover")
    sub.add_parser("stop")
    sub.add_parser("arm")
    upload = sub.add_parser("upload")
    upload.add_argument("file")
    power = sub.add_parser("power")
    power.add_argument("target", type=int)
    power.add_argument("module", choices=MODULES)
    power.add_argument("rails", type=int, choices=range(4), help="0 off, 1=5V, 2=20V, 3=both")
    rgb = sub.add_parser("rgb")
    rgb.add_argument("target", type=int)
    rgb.add_argument("color", help="RRGGBB")
    gate = sub.add_parser("gate")
    gate.add_argument("target", type=int)
    gate.add_argument("open", type=int, choices=[0, 1])
    lift = sub.add_parser("lift")
    lift.add_argument("target", type=int)
    lift.add_argument("action", choices=["stop", "run", "clear"])
    lift.add_argument("--duty", type=int, default=0)
    lift.add_argument("--duration", type=float, default=3, help="supervised run seconds, at most 10")
    args = parser.parse_args()
    connection = Connection(args.port)
    try:
        if args.command == "discover":
            connection.send(36)
            for packet in connection.packets(3):
                if packet["type"] == 8 and len(packet["data"]) == 24:
                    payload = packet["data"]
                    print(json.dumps({"address": packet["source"], "uid": payload[:12].hex(),
                                      "neighbors": struct.unpack("<6H", payload[12:])}))
        elif args.command == "upload":
            with open(args.file) as source:
                document = json.load(source)
            image = program(document)
            connection.request(32)
            for module in document.get("modules", []):
                connection.request(7, bytes([MODULES[module["type"]], module["rails"]]), module["address"])
            for offset in range(0, len(image), 46):
                connection.request(33, struct.pack("<H", offset) + image[offset:offset + 46])
            if not connection.request(34):
                raise RuntimeError("program storage not available")
        elif args.command == "stop":
            connection.request(5)
        elif args.command == "arm":
            connection.request(35, b"\1")
        elif args.command == "power":
            connection.request(7, bytes([MODULES[args.module], args.rails]), args.target)
        elif args.command == "rgb":
            color = bytes.fromhex(args.color)
            if len(color) != 3:
                raise ValueError("color must contain six hexadecimal digits")
            connection.request(2, color, args.target)
        elif args.command == "gate":
            connection.request(4, bytes([args.open]), args.target)
        elif args.command == "lift":
            if not 0 <= args.duty <= 180:
                raise ValueError("duty must be between 0 and 180")
            action = {"stop": 0, "run": 1, "clear": 2}[args.action]
            if action == 1:
                if not 0 < args.duration <= 10 or not args.duty:
                    raise ValueError("run requires positive duty and duration <=10 seconds")
                deadline = time.monotonic() + args.duration
                try:
                    while time.monotonic() < deadline:
                        connection.request(10, bytes([1, args.duty]), args.target)
                        select.select([], [], [], .15)
                finally:
                    connection.request(10, b"\0\0", args.target)
            else:
                connection.request(10, bytes([action, args.duty]), args.target)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
