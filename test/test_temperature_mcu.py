# ABOUTME: Unit tests for klippy/extras/temperature_mcu.py calibration on
# ABOUTME: the stm32c5, run against the module's real _build_config path.
import pytest

from klippy.extras import temperature_mcu

# Factory calibration words (raw 12-bit ADC readings at VDDA = 3.3V)
TS_CAL1_ADDR, TS_CAL2_ADDR = 0x08FFF814, 0x08FFF818


class _FakeQuery:
    def __init__(self, memory):
        self.memory = memory
        self.reads = []

    def send(self, data):
        order, addr = data
        self.reads.append((order, addr))
        return {"val": self.memory[addr]}


class _FakeMCU:
    def __init__(self, mcu_type, memory):
        self.mcu_type = mcu_type
        self.query = _FakeQuery(memory)

    def lookup_query_command(self, msgformat, respformat):
        return self.query

    def get_constants(self):
        return {"MCU": self.mcu_type}

    def get_name(self):
        return "mcu"


class _FakeADC:
    def __init__(self, mcu):
        self.mcu = mcu

    def get_mcu(self):
        return self.mcu

    def setup_minmax(self, *args, **kwargs):
        pass

    def _build_config(self):
        pass


def _make_sensor(mcu_type, memory):
    cls = temperature_mcu.PrinterTemperatureMCU
    sensor = cls.__new__(cls)
    sensor.reference_voltage = 3.3
    sensor.temp1 = sensor.adc1 = sensor.temp2 = sensor.adc2 = None
    sensor.min_temp, sensor.max_temp = 0.0, 100.0
    sensor._danger_check_count = 4
    sensor.mcu_adc = _FakeADC(_FakeMCU(mcu_type, memory))
    return sensor


@pytest.mark.parametrize("mcu_type", ["stm32c551xx", "stm32c552xx"])
def test_stm32c5_maps_calibration_points(mcu_type):
    sensor = _make_sensor(mcu_type, {TS_CAL1_ADDR: 1000, TS_CAL2_ADDR: 1400})
    sensor._build_config()
    assert sensor.calc_adc(30.0) == pytest.approx(1000 / 4095.0)
    assert sensor.calc_adc(140.0) == pytest.approx(1400 / 4095.0)


def test_stm32c5_reads_calibration_as_halfwords():
    sensor = _make_sensor(
        "stm32c552xx", {TS_CAL1_ADDR: 1000, TS_CAL2_ADDR: 1400}
    )
    sensor._build_config()
    # order 1 is a 16-bit read; byte reads of this area fault on stm32c5
    assert sensor.mcu_adc.mcu.query.reads == [
        (1, TS_CAL1_ADDR),
        (1, TS_CAL2_ADDR),
    ]
