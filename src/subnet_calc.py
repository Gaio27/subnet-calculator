"""Fungsi inti kalkulator subnet dan VLSM."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class SubnetInfo:
    network: ipaddress.IPv4Network
    broadcast: ipaddress.IPv4Address
    netmask: ipaddress.IPv4Address
    first_host: ipaddress.IPv4Address | None
    last_host: ipaddress.IPv4Address | None
    usable_hosts: int


@dataclass(frozen=True)
class VlsmAllocation:
    requested: int
    network: ipaddress.IPv4Network
    usable_hosts: int


def parse_network(cidr: str) -> ipaddress.IPv4Network:
    """Mengubah teks CIDR menjadi jaringan IPv4. Alamat host (bukan alamat jaringan) juga diterima."""
    return ipaddress.IPv4Network(cidr, strict=False)


def usable_hosts(prefix: int) -> int:
    """Jumlah host yang bisa dipakai. /31 dan /32 mengikuti RFC 3021 dan praktik umum."""
    if prefix == 32:
        return 1
    if prefix == 31:
        return 2
    return 2 ** (32 - prefix) - 2


def info(cidr: str) -> SubnetInfo:
    net = parse_network(cidr)
    if net.prefixlen >= 31:
        first, last = None, None
        if net.prefixlen == 31:
            first, last = net.network_address, net.broadcast_address
        else:
            first = last = net.network_address
    else:
        first = net.network_address + 1
        last = net.broadcast_address - 1
    return SubnetInfo(
        network=net,
        broadcast=net.broadcast_address,
        netmask=net.netmask,
        first_host=first,
        last_host=last,
        usable_hosts=usable_hosts(net.prefixlen),
    )


def prefix_for_hosts(needed: int) -> int:
    """Prefix terkecil yang memuat `needed` host dengan dua alamat cadangan (jaringan dan broadcast)."""
    if needed < 1:
        raise ValueError("Jumlah host harus minimal 1")
    total = needed + 2
    if total > 2**32:
        raise ValueError("Jumlah host terlalu besar untuk IPv4")
    host_bits = (total - 1).bit_length()
    prefix = 32 - host_bits
    if needed == 1:
        return 32
    if needed == 2:
        return 30
    return prefix


def vlsm(parent_cidr: str, needs: list[int]) -> list[VlsmAllocation]:
    """Membagi blok induk ke beberapa kebutuhan host, dari yang terbesar ke terkecil.

    Setiap subnet dimulai pada alamat yang sejajar dengan ukuran bloknya, sehingga tidak ada celah
    yang salah bentuk. Hasil dikembalikan sesuai urutan alokasi.
    """
    if not needs:
        raise ValueError("Daftar kebutuhan host kosong")
    parent = parse_network(parent_cidr)
    ordered = sorted(needs, reverse=True)
    cursor = int(parent.network_address)
    end = int(parent.broadcast_address)
    results: list[VlsmAllocation] = []
    for need in ordered:
        prefix = prefix_for_hosts(need)
        size = 2 ** (32 - prefix)
        # Geser cursor ke kelipatan ukuran blok
        if cursor % size:
            cursor += size - (cursor % size)
        if cursor + size - 1 > end:
            raise ValueError(
                f"Blok {parent} tidak cukup untuk kebutuhan {need} host"
            )
        net = ipaddress.IPv4Network((cursor, prefix))
        results.append(VlsmAllocation(requested=need, network=net, usable_hosts=usable_hosts(prefix)))
        cursor += size
    return results


def overlaps(a_cidr: str, b_cidr: str) -> bool:
    return parse_network(a_cidr).overlaps(parse_network(b_cidr))
