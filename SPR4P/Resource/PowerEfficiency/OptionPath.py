from SPR4P.Config.PlatConfig import Msg

integer = ['Current Under Report', 'CPU Frequency Select']
key_up = ['Hardware P-State', 'Power Performance Tuning', "NUMA", 'Page Policy', 'Uncore Freq Scaling']
less_try = ['EPP Enable', 'CPU Frequency Select', 'ENERGY_PERF_BIAS_CFG mode']


MENU_OPTIONS = [

    [Msg.PATH_PRO_CFG, [
        'Enable LP \[Global\]',
        'Hardware Prefetcher',
        'Adjacent Cache Prefetch',
        'DCU Streamer Prefetcher',
        'DCU IP Prefetcher',
        'LLC Prefetch',
    ]],

    [[Msg.CPU_CONFIG, Msg.COMMON_REF_CONFIG], [
        # 'ISOC Mode'  # 隐藏
        'NUMA',
    ]],

    [Msg.PATH_UNCORE_GENERAL, [
        'Link Frequency Select',
        'Link L0p Enable',
        'Link L1 Enable',
        'KTI Prefetch',
        'Local/Remote Threshold',
        'XPT Prefetch',
        'LLC dead line alloc',
    ]],

    [Msg.PATH_MEM_CONFIG, [
        'DDR PPR Type',
        'Attempt Fast Cold Boot',
        'Custom Refresh Enable',
        'Custom Refresh Rate',
        'Refresh Options',
        # 'Partial Cache Line Sparing PCLS',
    ]],

    [Msg.PATH_MEM_CONFIG + ["Page Policy"], [
        'Page Policy',
    ]],

    [Msg.PATH_MEM_CONFIG + [Msg.MEM_RAS_CFG], [
        'ADDDC Sparing',
        # 'Patrol Scrubbing',  # 隐藏不上报

    ]],

    [Msg.PATH_ADV_PM_CFG, [
        'DEMT',
        'Static Turbo',
        'CPU Frequency Select',
    ]],

    [Msg.PATH_ADV_PM_CFG + [Msg.CPU_P_STATE], [
        'SpeedStep \(Pstates\)',
        'EIST PSD Function',
        'Boot performance mode',
        'Energy Efficient Turbo',
        'Turbo Mode',
        'CPU Flex Ratio Override',
    ]],

    [Msg.PATH_ADV_PM_CFG + [Msg.HW_P_STATE], [
        'Hardware P-State',
        'EPP Enable',
        'EPP Profile',
    ]],

    [Msg.PATH_ADV_PM_CFG + [Msg.CPU_C_STATE], [
        'CPU C6 report',
        'Enhanced Halt State \(C1E\)',
        'Enable Monitor MWAIT',
    ]],

    [Msg.PATH_ADV_PM_CFG + [Msg.PKG_C_STATE_CONTROL], [
        'Package C-State',
    ]],

    [Msg.PATH_ADV_PM_CFG + [Msg.CPU_ADV_PM_TUN], [
        'Uncore Freq Scaling',
    ]],

    [Msg.PATH_ADV_PM_CFG + [Msg.CPU_ADV_PM_TUN, "Energy Perf BIAS"],
     [
        'Power Performance Tuning',
        'ENERGY_PERF_BIAS_CFG mode',
    ]],

    [Msg.PATH_MEM_POWER_ADV, [
        'CKE Power Down',
    ]],

    [[Msg.MISC_CONFIG], [
        'Current Under Report',
    ]],

    [[Msg.SYS_EVENT_LOG], [
        'System Errors',
        'System Memory Poisoning',
        'FDM',
    ]],

    # [[], [
    #     'Extreme Edition',
    #     'UFS'
    # ]]

]
