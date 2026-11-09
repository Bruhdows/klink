import importlib.util
import pathlib
import unittest
spec = importlib.util.spec_from_file_location("client", pathlib.Path(__file__).parents[1]/"tools/klink.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)

class ClientTests(unittest.TestCase):
    def test_all_payload_lengths_and_zero_runs(self):
        for n in range(49):
            for byte in range(256):
                payload = bytes([byte])*n
                wire = client.encode(2, payload, 0xffff, 0xffff)
                self.assertLessEqual(len(wire), 62)
                self.assertEqual(client.decode(wire[:-1])["data"], payload)

    def test_crc_and_program(self):
        self.assertEqual(client.crc(b"123456789"), 0x29b1)
        image = client.program({"rules": [{"source": 3, "target": 4, "event": 1,
                                           "action": "gate", "data": [1]}]})
        self.assertEqual(len(image), 200)
        self.assertEqual(image[:4], b"KL\1\1")
        self.assertEqual(int.from_bytes(image[-2:], "little"), client.crc(image[:-2]))
        with self.assertRaises(ValueError):
            client.program({"rules": [{"source": 3, "target": 4, "event": 1,
                                        "action": "gate", "data": [2]}]})

    def test_invalid_frames(self):
        for wire in [b"", b"\0", b"\x05abc", b"\1"*62]:
            with self.assertRaises(ValueError):
                client.decode(wire)

if __name__ == "__main__":
    unittest.main()
