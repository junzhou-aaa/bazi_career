from datetime import datetime
from lunar_python import Solar, Lunar
from lunar_python.util import LunarUtil
from .models import Chart, Pillar, Sex

def _get_ten_god(day_master: str, target: str) -> str:
    """Get the Ten God (十神) for a given target stem/branch against the day master."""
    # The dictionary in LunarUtil is structured such that SHI_SHEN[day_master + target] = ten_god
    return LunarUtil.SHI_SHEN.get(day_master + target, "")

def _get_yin_yang(char: str) -> str:
    """Get Yin/Yang classification for a stem or branch."""
    if char in LunarUtil.GAN:
        idx = LunarUtil.GAN.index(char)
        return "阳" if idx % 2 == 1 else "阴"
    elif char in LunarUtil.ZHI:
        idx = LunarUtil.ZHI.index(char)
        return "阳" if idx % 2 == 1 else "阴"
    return "未知"

def _get_five_elements(char: str) -> str:
    """Get Five Elements (五行) for a stem or branch."""
    # WU_XING is usually mapping Gan and Zhi to elements, but let's just map manually if needed, or use LunarUtil
    if char in LunarUtil.GAN:
        return LunarUtil.WU_XING_GAN.get(char, "")
    elif char in LunarUtil.ZHI:
        return LunarUtil.WU_XING_ZHI.get(char, "")
    return ""

def _five_tiger_month_stem(year_stem: str, month_branch: str) -> str:
    """五虎遁: calculate month stem based on year stem and month branch."""
    # Month branches start from Yin (index 3). Year stems shift the starting stem.
    # Year Stem: 甲己 -> 丙寅, 乙庚 -> 戊寅, 丙辛 -> 庚寅, 丁壬 -> 壬寅, 戊癸 -> 甲寅
    start_stem_idx = {
        '甲': '丙', '己': '丙',
        '乙': '戊', '庚': '戊',
        '丙': '庚', '辛': '庚',
        '丁': '壬', '壬': '壬',
        '戊': '甲', '癸': '甲'
    }
    yin_idx = 3 # 寅
    branch_idx = LunarUtil.ZHI.index(month_branch)
    if branch_idx < yin_idx:
        branch_idx += 12
    offset = branch_idx - yin_idx
    
    start_stem = start_stem_idx.get(year_stem, '甲')
    stem_idx = LunarUtil.GAN.index(start_stem)
    
    final_stem_idx = (stem_idx - 1 + offset) % 10 + 1
    return LunarUtil.GAN[final_stem_idx]

def calculate_chart(profile_id: str, dt_true_solar: datetime, sex: Sex, is_southern: bool, known_time: bool = True) -> Chart:
    """
    Calculate the Four Pillars chart, properly handling Southern Hemisphere and missing time.
    """
    solar = Solar.fromYmdHms(
        dt_true_solar.year, 
        dt_true_solar.month, 
        dt_true_solar.day,
        dt_true_solar.hour if known_time else 0,
        dt_true_solar.minute if known_time else 0,
        dt_true_solar.second if known_time else 0
    )
    lunar = solar.getLunar()
    ba_zi = lunar.getEightChar()
    
    # 1. Base pillars
    year_gan = ba_zi.getYearGan()
    year_zhi = ba_zi.getYearZhi()
    
    month_gan = ba_zi.getMonthGan()
    month_zhi = ba_zi.getMonthZhi()
    
    day_gan = ba_zi.getDayGan()
    day_zhi = ba_zi.getDayZhi()
    
    hour_gan = ba_zi.getTimeGan() if known_time else None
    hour_zhi = ba_zi.getTimeZhi() if known_time else None
    
    # 2. Apply Southern Hemisphere adjustment if needed
    if is_southern:
        # Shift month branch by 6
        zhi_idx = LunarUtil.ZHI.index(month_zhi)
        new_zhi_idx = (zhi_idx - 1 + 6) % 12 + 1
        month_zhi = LunarUtil.ZHI[new_zhi_idx]
        
        # Recalculate month stem using 五虎遁
        month_gan = _five_tiger_month_stem(year_gan, month_zhi)
        
    year_pillar = Pillar(stem=year_gan, branch=year_zhi)
    month_pillar = Pillar(stem=month_gan, branch=month_zhi)
    day_pillar = Pillar(stem=day_gan, branch=day_zhi)
    hour_pillar = Pillar(stem=hour_gan, branch=hour_zhi) if known_time else None
    
    day_master = day_gan
    month_order = month_zhi
    
    # 3. Hidden Stems
    hidden_stems = {
        year_zhi: LunarUtil.ZHI_HIDE_GAN.get(year_zhi, []),
        month_zhi: LunarUtil.ZHI_HIDE_GAN.get(month_zhi, []),
        day_zhi: LunarUtil.ZHI_HIDE_GAN.get(day_zhi, [])
    }
    if known_time and hour_zhi:
        hidden_stems[hour_zhi] = LunarUtil.ZHI_HIDE_GAN.get(hour_zhi, [])
        
    # 4. Ten Gods, Five Elements, Yin Yang
    ten_gods = {}
    five_elements = {}
    yin_yang = {}
    
    chars = [year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi]
    if known_time:
        chars.extend([hour_gan, hour_zhi])
        
    for c in chars:
        if c not in ten_gods and c != day_master:
            ten_gods[c] = _get_ten_god(day_master, c)
            
        if c not in five_elements:
            five_elements[c] = _get_five_elements(c)
            
        if c not in yin_yang:
            yin_yang[c] = _get_yin_yang(c)
            
    # For hidden stems, calculate Ten Gods too
    for branch, stems in hidden_stems.items():
        for s in stems:
            if s not in ten_gods and s != day_master:
                ten_gods[s] = _get_ten_god(day_master, s)
                
    # 5. Luck Cycles (大运)
    gender_code = 1 if sex == Sex.MALE else 0 # 1 for male, 0 for female
    yun = ba_zi.getYun(gender_code)
    
    luck_direction = "顺" if yun.isForward() else "逆"
    start_of_luck = yun.getStartYear()
    
    da_yuns = yun.getDaYun()
    luck_cycles = []
    for dy in da_yuns:
        gan_zhi = dy.getGanZhi()
        if not gan_zhi:
            continue
        luck_cycles.append({
            "age": dy.getStartAge(),
            "year": dy.getStartYear(),
            "pillar": {"stem": gan_zhi[0], "branch": gan_zhi[1]}
        })
        
    # 6. Apply Southern Hemisphere to Luck Cycles if needed
    if is_southern:
        # DaYun depends on month pillar, so we need to reconstruct them based on the new month pillar
        # Standard rules: Shun = next stem/branch, Ni = previous stem/branch
        shun = yun.isForward()
        current_gan_idx = LunarUtil.GAN.index(month_gan)
        current_zhi_idx = LunarUtil.ZHI.index(month_zhi)
        
        adjusted_luck_cycles = []
        for dy in da_yuns:
            if shun:
                current_gan_idx = (current_gan_idx - 1 + 1) % 10 + 1
                current_zhi_idx = (current_zhi_idx - 1 + 1) % 12 + 1
            else:
                current_gan_idx = (current_gan_idx - 1 - 1) % 10 + 1
                current_zhi_idx = (current_zhi_idx - 1 - 1) % 12 + 1
                
            adjusted_luck_cycles.append({
                "age": dy.getStartAge(),
                "year": dy.getStartYear(),
                "pillar": {"stem": LunarUtil.GAN[current_gan_idx], "branch": LunarUtil.ZHI[current_zhi_idx]}
            })
        luck_cycles = adjusted_luck_cycles
        
    return Chart(
        id=f"chart_{profile_id}",
        profile_id=profile_id,
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        day_master=day_master,
        month_order=month_order,
        hidden_stems=hidden_stems,
        ten_gods=ten_gods,
        five_elements=five_elements,
        yin_yang=yin_yang,
        luck_direction=luck_direction,
        start_of_luck=start_of_luck,
        luck_cycles=luck_cycles,
        model_version="1.0.0",
        created_at=datetime.now().isoformat()
    )
