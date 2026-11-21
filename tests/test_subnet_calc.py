import ipaddress
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import subnet_calc as sc  # noqa: E402


def test_info_slash26():
    i = sc.info("192.168.10.0/26")
    assert str(i.broadcast) == "192.168.10.63"
    assert str(i.netmask) == "255.255.255.192"
    assert str(i.first_host) == "192.168.10.1"
    assert str(i.last_host) == "192.168.10.62"
    assert i.usable_hosts == 62


def test_info_slash30_has_two_hosts():
    assert sc.info("10.0.0.0/30").usable_hosts == 2


def test_info_slash31_point_to_point():
    i = sc.info("10.0.0.0/31")
    assert i.usable_hosts == 2


def test_info_slash32_single_host():
    i = sc.info("10.0.0.5/32")
    assert i.usable_hosts == 1
    assert str(i.first_host) == "10.0.0.5"


def test_info_accepts_host_address_and_normalizes():
    i = sc.info("192.168.10.77/26")
    assert str(i.network.network_address) == "192.168.10.64"


def test_prefix_for_hosts_boundaries():
    assert sc.prefix_for_hosts(1) == 32
    assert sc.prefix_for_hosts(2) == 30
    assert sc.prefix_for_hosts(14) == 28   # 14 host muat di /28
    assert sc.prefix_for_hosts(15) == 27   # 15 host tidak muat di /28
    assert sc.prefix_for_hosts(254) == 24
    assert sc.prefix_for_hosts(255) == 23


def test_prefix_for_hosts_rejects_zero():
    with pytest.raises(ValueError):
        sc.prefix_for_hosts(0)


def test_vlsm_matches_readme_example():
    result = sc.vlsm("10.10.0.0/16", [10, 500, 50, 200])
    got = [str(a.network) for a in result]
    assert got == [
        "10.10.0.0/23",     # 500 host
        "10.10.2.0/24",     # 200 host
        "10.10.3.0/26",     # 50 host
        "10.10.3.64/28",    # 10 host
    ]
    assert [a.requested for a in result] == [500, 200, 50, 10]


def test_vlsm_allocations_do_not_overlap():
    result = sc.vlsm("172.16.0.0/16", [100, 60, 30, 30, 5, 2])
    nets = [a.network for a in result]
    for i in range(len(nets)):
        for j in range(i + 1, len(nets)):
            assert not nets[i].overlaps(nets[j])


def test_vlsm_fails_when_block_too_small():
    with pytest.raises(ValueError):
        sc.vlsm("10.0.0.0/25", [100, 100])


def test_vlsm_rejects_empty_list():
    with pytest.raises(ValueError):
        sc.vlsm("10.0.0.0/24", [])


def test_overlaps():
    assert sc.overlaps("10.0.0.0/24", "10.0.0.128/25")
    assert not sc.overlaps("10.0.0.0/24", "10.0.1.0/24")
