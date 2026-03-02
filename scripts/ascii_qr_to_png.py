#!/usr/bin/env python3
"""Konvertiert OpenClaw ASCII-QR (stdin oder Datei) in eine scannbare PNG.
Nutzt nur Standardbibliothek (zlib, struct) - kein Pillow."""
import sys
import zlib
import struct

def is_qr_line(line: str) -> bool:
    """Zeilen die wie QR-ASCII aussehen (Blockzeichen oder Encoding-Fehler)."""
    stripped = line.strip()
    if not stripped or len(stripped) < 10:
        return False
    return any(ord(c) > 127 for c in stripped)


def write_png(buf: bytes, width: int, height: int, path: str) -> None:
    """Schreibt 8-bit Graustufen-PNG (buf = Zeile für Zeile, 0=schwarz)."""
    raw = b"".join(
        buf[span : span + width]
        for span in range((height - 1) * width, -1, -width)
    )
    compressed = zlib.compress(raw, 9)

    def png_pack(tag: bytes, data: bytes) -> bytes:
        chunk = tag + data
        return (
            struct.pack("!I", len(data))
            + chunk
            + struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk))
        )

    header = struct.pack(
        "!2I5B", width, height, 8, 0, 0, 0, 0
    )  # 8bit grayscale
    png = b"".join([
        b"\x89PNG\r\n\x1a\n",
        png_pack(b"IHDR", header),
        png_pack(b"IDAT", compressed),
        png_pack(b"IEND", b""),
    ])
    with open(path, "wb") as f:
        f.write(png)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        with open(sys.argv[2], "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    lines = [l.rstrip("\n") for l in raw.splitlines() if is_qr_line(l)]
    if not lines:
        print("Keine QR-ASCII-Zeilen gefunden.", file=sys.stderr)
        sys.exit(1)

    h, w = len(lines), max(len(l) for l in lines)
    # Terminal-ASCII: typisch 2 Zeichen pro horizontales QR-Modul (Zeichen sind schmal).
    # → modules_wide = w/2, modules_high = h. Quadrat: N = min(h, w//2).
    n = min(h, w // 2)  # QR-Seitenlänge in Modulen
    if n < 10:
        n = min(h, w)
    cell = 8  # Pixel pro Modul (am Ende quadratisch: n*cell x n*cell)
    out_w = out_h = n * cell
    buf = bytearray(out_w * out_h)
    for py in range(n):
        for px in range(n):
            # ASCII: Zeile py, Spalte 2*px (evtl. 2*px+1) = 1 Modul
            y, x0 = py, 2 * px
            line = lines[y] if y < len(lines) else ""
            c1 = line[x0] if x0 < len(line) else " "
            c2 = line[x0 + 1] if x0 + 1 < len(line) else " "
            is_black = c1 != " " or c2 != " "
            for dy in range(cell):
                for dx in range(cell):
                    nx, ny = px * cell + dx, py * cell + dy
                    if nx < out_w and ny < out_h:
                        buf[ny * out_w + nx] = 0 if is_black else 255

    out = "openclaw_whatsapp_qr.png"
    write_png(bytes(buf), out_w, out_h, out)
    print(out)


if __name__ == "__main__":
    main()
