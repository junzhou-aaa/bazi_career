from datetime import datetime
from bazi_career.domain.astrology.calendar import calculate_true_solar_time, get_equation_of_time
from bazi_career.domain.astrology.pillars import calculate_chart
from bazi_career.domain.astrology.models import Sex

def test_equation_of_time():
    # Example from PRP: 2000-08-01 should be approx -6m16s
    dt = datetime(2000, 8, 1, 12, 0, 0)
    eot = get_equation_of_time(dt)
    assert abs(eot - (-6.26)) < 1.0 # Within 1 min tolerance

def test_true_solar_time():
    dt_local = datetime(2000, 8, 1, 12, 0, 0)
    # Stockholm is timezone Europe/Stockholm
    tst = calculate_true_solar_time(dt_local, 18.06, "Europe/Stockholm")
    
    # DST was active (+2 UTC), standard is +1 UTC (15 degrees E)
    # Deduct DST: 12:00 -> 11:00 LMT base
    # Longitude difference: 18.06 - 15.0 = 3.06 degrees = +12.24 minutes
    # EoT on Aug 1 is approx -6.25 mins
    # True solar time = 11:00 + 12.24 - 6.25 = 11:05:59 approx
    
    # 12:00 local time = 10:00 UTC. 
    # Let's check hour
    assert tst.hour == 11
    assert 5 <= tst.minute <= 7

def test_calculate_chart_northern():
    dt = datetime(2000, 8, 1, 11, 12, 14) # A calculated TST
    chart = calculate_chart("test1", dt, Sex.MALE, is_southern=False, known_time=True)
    assert chart.year_pillar.stem == "庚"
    assert chart.year_pillar.branch == "辰"
    assert chart.month_pillar.stem == "癸"
    assert chart.month_pillar.branch == "未"
    assert chart.day_pillar.stem == "辛"
    assert chart.day_pillar.branch == "卯"
    assert chart.hour_pillar.stem == "甲"
    assert chart.hour_pillar.branch == "午"

def test_calculate_chart_southern():
    dt = datetime(2000, 8, 1, 11, 12, 14)
    # Southern should reverse month branch from 未(8) to 丑(2)
    # Year stem is 庚. Start stem for year 庚 is 戊(寅).
    # Month branch 丑 is index 2, 寅 is index 3. 丑 is before 寅 so +12 -> 14.
    # offset = 14 - 3 = 11. 
    # Start stem index for 戊 is 5.
    # final stem = (5 - 1 + 11) % 10 + 1 = 15 % 10 + 1 = 6 (己)
    chart = calculate_chart("test1", dt, Sex.MALE, is_southern=True, known_time=True)
    assert chart.month_pillar.branch == "丑"
    assert chart.month_pillar.stem == "己"
    
    # Let's check: year 庚. 戊寅(1), 己卯(2), 庚辰(3), 辛巳(4), 壬午(5), 癸未(6), 甲申(7), 乙酉(8), 丙戌(9), 丁亥(10), 戊子(11), 己丑(12)
    # So branch 丑 corresponds to 己! Wait, the 12th month of year 庚 is 己丑.
    # But wait, is it 己丑 or 丁丑?
    # Let's see what the code actually outputs, then we can adjust assertion or fix logic.
