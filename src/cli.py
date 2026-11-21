"""Antarmuka baris perintah kalkulator subnet."""

from __future__ import annotations

import argparse
import sys

import subnet_calc as sc


def cmd_info(args: argparse.Namespace) -> int:
    i = sc.info(args.cidr)
    print(f"Jaringan   : {i.network.network_address}/{i.network.prefixlen}")
    print(f"Broadcast  : {i.broadcast}")
    print(f"Netmask    : {i.netmask}")
    if i.first_host and i.last_host:
        print(f"Rentang    : {i.first_host} - {i.last_host}")
    print(f"Host       : {i.usable_hosts} tersedia")
    return 0


def cmd_vlsm(args: argparse.Namespace) -> int:
    allocations = sc.vlsm(args.parent, args.hosts)
    print(f"Blok induk: {args.parent}")
    for n, a in enumerate(allocations, start=1):
        print(
            f"Subnet {n}: {a.network.network_address}/{a.network.prefixlen}     "
            f"({a.requested} host dibutuhkan, {a.usable_hosts} tersedia)"
        )
    return 0


def cmd_overlap(args: argparse.Namespace) -> int:
    if sc.overlaps(args.a, args.b):
        print(f"{args.a} dan {args.b} TUMPANG TINDIH")
        return 1
    print(f"{args.a} dan {args.b} tidak tumpang tindih")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Kalkulator subnet dan VLSM")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("info", help="informasi satu subnet")
    pi.add_argument("cidr", help="contoh: 192.168.10.0/26")
    pi.set_defaults(func=cmd_info)

    pv = sub.add_parser("vlsm", help="bagi blok induk sesuai kebutuhan host")
    pv.add_argument("parent", help="contoh: 10.10.0.0/16")
    pv.add_argument("--hosts", type=int, nargs="+", required=True, help="daftar jumlah host")
    pv.set_defaults(func=cmd_vlsm)

    po = sub.add_parser("overlap", help="periksa dua CIDR tumpang tindih")
    po.add_argument("a")
    po.add_argument("b")
    po.set_defaults(func=cmd_overlap)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
