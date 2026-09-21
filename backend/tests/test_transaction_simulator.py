from datetime import datetime, timezone

from app.services.transaction_simulator import TransactionSimulator


def test_simulator_is_reproducible():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    simulator = TransactionSimulator(seed=7)

    first = simulator.generate(days=3, start_date=start)
    second = simulator.generate(days=3, start_date=start)

    assert first.equals(second)
    assert len(first) > 0
    assert first["source_record_id"].is_unique


def test_simulator_scenarios_inject_controlled_events():
    simulator = TransactionSimulator(seed=7)

    normal = simulator.generate(days=10, scenario="normal")
    abnormal = simulator.generate(days=10, scenario="abnormal_adjustment")
    delayed = simulator.generate(days=10, scenario="supplier_delay")

    assert "ADJUSTMENT" not in set(normal["event_type"])
    assert "SIM-ABNORMAL-ADJUSTMENT" in set(abnormal["reference_number"])
    assert len(delayed) < len(normal)
