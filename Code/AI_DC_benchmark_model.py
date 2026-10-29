# This file is a modified version of an open-source model posted at https://github.com/nuoaleon/Data-Center-Water-footprint, in which the immersion cooling systems are specifically defined.
import numpy as np
import pandas as pd
from typing import Optional

from scipy.optimize import *
from CoolProp.HumidAirProp import HAPropsSI

import pickle

# COP: based on gp regressor
# for water-cooled chiller
COP_gp = pickle.load(open(r'C:\Users\xiaot\AppData\Roaming\Python\Python39\site-packages\COP_2.pkl', 'rb'))
# for DX system
COP_DX_gp = pickle.load(open(r'C:\Users\xiaot\AppData\Roaming\Python\Python39\site-packages\COP_DX.pkl', 'rb'))
# for air-cooled chiller
COP_air_gp = pickle.load(open(r'C:\Users\xiaot\AppData\Roaming\Python\Python39\site-packages\COP_AC.pkl', 'rb'))


# Other functions #

# (used for HDC_AE_Adiabatic)
def Air_side_economizer(T_up,T_lw,dp_up,dp_lw,RH_up,RH_lw,T_oa,RH_oa,P_oa,delta_T_air):
    # outside air enthalpy
    H_oa = HAPropsSI('H','T',T_oa+273.15,'P',P_oa,'RH',RH_oa/100)
    # outside air absolute humidity
    d_oa = HAPropsSI('W','T',T_oa+273.15,'RH',RH_oa/100,'P',P_oa)
    # outside air dewpoint
    dp_oa = HAPropsSI('Tdp','T',T_oa+273.15,'P',P_oa,'RH',RH_oa/100)-273.15
     
    # # # # (calculations)-------------------------------
    if (T_lw <= T_oa < T_up):
        # absolute humidity range:
        d_up = np.minimum(HAPropsSI('W','T',T_oa+273.15,'RH',RH_up/100,'P',P_oa),HAPropsSI('W','T',T_oa+273.15,'Tdp',dp_up+273.15,'P',P_oa))
        d_lw = np.maximum(HAPropsSI('W','T',T_oa+273.15,'RH',RH_lw/100,'P',P_oa),HAPropsSI('W','T',T_oa+273.15,'Tdp',dp_lw+273.15,'P',P_oa))
        if (d_lw <= d_oa <= d_up): # *checked*
            AE_use = 1
            HD_use = 0
            Steam_use = 0
            DHD_use = 0
            delta_d = 0
            d_sa = d_oa
            T_cd = T_oa
            H_cd = H_oa
            chiller_energy = 0
            heating_energy = 0
            T_sa = T_oa
            H_sa = H_oa            
        if (d_oa > d_up): # *checked*
            AE_use = 0
            HD_use = 0
            Steam_use = 0
            DHD_use = 1
            d_sa = d_up
            delta_d = d_oa - d_up
            T_cd = dp_up   
            H_cd = HAPropsSI('H','T',dp_up+273.15,'P',P_oa,'W',d_up)
            chiller_energy = H_oa - H_cd
            heating_energy = 0
            T_sa = np.maximum(T_lw, T_cd)   # mix air to low setpoint when required
            H_sa = HAPropsSI('H','T',T_sa+273.15,'P',P_oa,'W',d_up)
        if (d_oa < d_lw): # *checked*
            # if use adiabatic humidification (default)
            AE_use = 1
            HD_use = 1
            Steam_use = 0
            DHD_use = 0
            delta_d = d_lw - d_oa
            d_sa = d_lw
            H_cd = H_oa
            T_cd = HAPropsSI('T','H',H_oa,'W',d_lw,'P',P_oa)-273.15
            chiller_energy = 0
            heating_energy = 0
            T_sa = np.maximum(T_lw, T_cd)   # mix air to low setpoint when required
            H_sa = HAPropsSI('H','T',T_sa+273.15,'P',P_oa,'W',d_lw)
    
    if (T_oa < T_lw):
        # absolute humidity range:
        d_up = np.minimum(HAPropsSI('W','T',T_lw+273.15,'RH',RH_up/100,'P',P_oa),HAPropsSI('W','T',T_lw+273.15,'Tdp',dp_up+273.15,'P',P_oa))
        d_lw = np.maximum(HAPropsSI('W','T',T_lw+273.15,'RH',RH_lw/100,'P',P_oa),HAPropsSI('W','T',T_lw+273.15,'Tdp',dp_lw+273.15,'P',P_oa))
        if (d_oa < d_lw): # *checked*
            # if use adiabatic humidification (default)
            AE_use = 1
            HD_use = 1
            Steam_use = 0
            DHD_use = 0
            delta_d = d_lw - d_oa
            d_sa = d_lw
            H_cd = H_oa
            T_cd = HAPropsSI('T','H',H_oa,'W',d_lw,'P',P_oa)-273.15
            chiller_energy = 0
            heating_energy = 0
            T_sa = np.maximum(T_lw, T_oa)   # mix air to low setpoint when required
            H_sa = HAPropsSI('H','T',T_sa+273.15,'P',P_oa,'W',d_lw)
        if (d_lw <= d_oa <= d_up): # *checked*
            AE_use = 1
            HD_use = 0
            Steam_use = 0
            DHD_use = 0
            delta_d = 0
            d_sa = d_oa
            T_cd = T_oa 
            H_cd = H_oa
            chiller_energy = 0
            heating_energy = 0
            T_sa = np.maximum(T_lw, T_oa)   # mix air to low setpoint when required
            H_sa = HAPropsSI('H','T',T_sa+273.15,'P',P_oa,'W',d_oa) 
        if (d_oa > d_up): # *checked*
            d_up_at_upsasp = HAPropsSI('W','T',T_up+273.15,'Tdp',dp_up+273.15,'P',P_oa) # absolute humidity at upper bound temperature setpoint
            if (d_oa <= d_up_at_upsasp):
                AE_use = 1
                HD_use = 0
                Steam_use = 0
                DHD_use = 0
                delta_d = 0
                T_cd = T_oa
                d_sa = d_oa
                H_cd = H_oa
                chiller_energy = 0
                heating_energy = 0
                #y = lambda x: HAPropsSI('RH','T',T_oa+273.15+x,'P',P_oa,'W',d_oa) - RH_up/100  # find how mix with hot air could get the required RH
                #T_sa = fsolve(y,0)[0] + T_oa
                T_sa = T_lw
                H_sa = HAPropsSI('H','T',T_lw+273.15,'P',P_oa,'W',d_oa)
            else:  #*checked*
                AE_use = 1
                HD_use = 0
                Steam_use = 0
                DHD_use = 1
                delta_d = d_oa - d_up_at_upsasp
                T_cd = dp_up
                d_sa = d_up_at_upsasp
                H_cd = HAPropsSI('H','T',dp_up + 273.15,'P',P_oa,'W',d_up_at_upsasp)
                chiller_energy = np.maximum(H_cd - H_oa,0)  # a very small portion of time that requires dehumidifcation but enthalpy of air is low, sometimes th
                heating_energy = 0
                T_sa = np.maximum(T_lw, T_cd)   # mix air to low setpoint when required
                H_sa = HAPropsSI('H','T',T_sa+273.15,'P',P_oa,'W',d_up_at_upsasp) 
                
    if (T_oa >= T_up):
        # absolute humidity range:
        d_up = np.minimum(HAPropsSI('W','T',T_up+273.15,'RH',RH_up/100,'P',P_oa),HAPropsSI('W','T',T_up+273.15,'Tdp',dp_up+273.15,'P',P_oa))
        d_lw = np.maximum(HAPropsSI('W','T',T_up+273.15,'RH',RH_lw/100,'P',P_oa),HAPropsSI('W','T',T_up+273.15,'Tdp',dp_lw+273.15,'P',P_oa))
        # enthalpy threshold for evaporative cooling
        H_threshold_up = HAPropsSI('H','T',T_up+273.15,'P',P_oa,'W',d_up)
        H_threshold_lw = HAPropsSI('H','T',T_up+273.15,'P',P_oa,'W',d_lw)

        #...(new control policy: the old one was commented below because too optimistic)        
        AE_use = 0
        HD_use = 0
        Steam_use = 0
        DHD_use = 0
        T_cd = T_up
        H_cd = HAPropsSI('H','T',T_up+273.15,'P',P_oa,'W',d_up)
        d_sa = d_up #not useful here#
        delta_d = 0

        H_sa = H_cd
        H_ra = H_sa + 1.01*delta_T_air*1000
        
        chiller_energy = H_ra - H_cd
        heating_energy = 0
        T_sa = T_cd
        H_sa = H_cd
        H_oa = H_sa + 1.01*delta_T_air*1000 # treat return air as outside air because DC will use return air
    
    return AE_use, HD_use, DHD_use, Steam_use, delta_d, T_sa, H_sa, T_cd, H_cd, d_sa, H_oa, chiller_energy, heating_energy 


# (used for HDC_AE_Adiabatic, HDC_WE, Colo_AE, Colo_WE, Colo_Chiller)
def Cooling_Tower(T_oa,RH_oa,P_oa,AT_CT,Power_IT,Q,delta_T_CT,Windage_p,CC,LGRatio):
    # Enthalpy of outside air
    h_oa = HAPropsSI('H','T',T_oa+273.15,'P',P_oa,'R',RH_oa/100)
    # wetbulb temperature of outside air
    T_wb_oa = HAPropsSI('Twb','H',h_oa,'T',T_oa+273.15,'P',P_oa)-273.15
    # absolute humidity of outside air
    d_oa = HAPropsSI('W','H',h_oa,'R',RH_oa/100,'P',P_oa)
    # absolute humidity of outlet cooling tower air: saturated
    d_oasa = HAPropsSI('W','H',h_oa,'R',1,'P',P_oa)
    # fun: Latent heat of water
    Latent_heat_vaporization = lambda T_water: -0.0013*(T_water)**(2)-2.3097*(T_water)+2500.5
    # Mass flow rate of cooling tower water: m_CT, kg/s
    m_CT = Q/(4.184*delta_T_CT)
    # Average temperature of cooling tower water: 
    T_CT = T_wb_oa + AT_CT + delta_T_CT/2
    # Evaporated water:
    Water_CT_evaporated = Q/Latent_heat_vaporization(T_CT)
    # Mass-flow of cooling tower air
    #m_air = Water_CT_evaporated/(d_oasa-d_oa)
    m_air = Water_CT_evaporated/LGRatio
    # Drift loss water: 
    Water_CT_windage =  m_CT*Windage_p
    # Drain-off water:
    Water_CT_DF = np.maximum(Water_CT_evaporated/(CC-1)-Water_CT_windage, 0)
    WUE = (Water_CT_evaporated +  Water_CT_windage + Water_CT_DF)*3600/Power_IT
    if m_air == 0:
        ratio = 0
    else:
        ratio = m_CT/(m_air)
    return WUE, m_air, ratio, Water_CT_evaporated, Water_CT_windage, Water_CT_DF
    
def Dry_Cooler(T_oa, RH_oa, P_oa,AT_DC, Power_IT, Q,delta_T_water,epsilon=0.65,adiabatic=False,eta_ad=0.85,drift_p=0.0,CC=5.0):
    # Basic checks
    if delta_T_water <= 0:
        raise ValueError("delta_T_water must be > 0 [°C].")
    if not (0 < epsilon <= 1.0):
        raise ValueError("epsilon must be in (0, 1].")
    if adiabatic and not (0 <= eta_ad <= 1.0):
        raise ValueError("eta_ad must be in [0, 1].")

    # Moist air properties at outdoor condition
    h_oa = HAPropsSI('H', 'T', T_oa + 273.15, 'P', P_oa, 'R', RH_oa / 100.0)          # [J/kg_da]
    T_wb = HAPropsSI('Twb', 'H', h_oa, 'T', T_oa + 273.15, 'P', P_oa) - 273.15       # [°C]
    w_oa = HAPropsSI('W', 'H', h_oa, 'R', RH_oa / 100.0, 'P', P_oa)                  # [kg_w/kg_da]

    # Inlet air to the coil: dry or adiabatically pre-cooled
    if adiabatic:
        # Pre-cooled dry-bulb via saturation effectiveness toward wet-bulb
        T_air_in_coil = T_oa - eta_ad * (T_oa - T_wb)

        # Approximate evaporative process as ~constant enthalpy (adiabatic humidification)
        w_in_coil = HAPropsSI('W', 'H', h_oa, 'T', T_air_in_coil + 273.15, 'P', P_oa)
        w_in_coil = max(w_in_coil, w_oa)  # ensure non-negative evaporation
    else:
        T_air_in_coil = T_oa
        w_in_coil = w_oa

    # Moist-air cp per kg dry air (kJ/kg_da-K), common approximation
    # cp_ma ≈ 1.006 + 1.86*w  (kJ/kg_da-K)
    cp_air = 1.006 + 1.86 * w_in_coil  # [kJ/kg_da-K]

    # Water flow from heat balance (kW = kJ/s)
    cp_water = 4.184  # [kJ/kg-K]
    m_water = Q / (cp_water * delta_T_water)  # [kg/s]

    # Define water temperatures using approach concept
    T_water_out = T_air_in_coil + AT_DC                 # cold/supply out of dry cooler [°C]
    T_water_in  = T_water_out + delta_T_water           # hot/return into dry cooler [°C]

    # Air temperature rise across coil using an effectiveness-like closure
    delta_T_air = epsilon * (T_water_in - T_air_in_coil)
    if delta_T_air <= 0:
        raise ValueError("Computed delta_T_air <= 0; check AT_DC, delta_T_water, epsilon, and ambient conditions.")

    # Required dry-air mass flow
    m_air = Q / (cp_air * delta_T_air)  # [kg_da/s]

    # Water use
    if adiabatic:
        Water_evap = m_air * (w_in_coil - w_oa)                     # [kg/s]
        Water_drift = Water_evap * max(drift_p, 0.0)                # [kg/s]
        if CC is not None and CC > 1.0:
            Water_blowdown = max(Water_evap / (CC - 1.0) - Water_drift, 0.0)
        else:
            Water_blowdown = 0.0
        Water_total = Water_evap + Water_drift + Water_blowdown
    else:
        Water_evap = 0.0
        Water_drift = 0.0
        Water_blowdown = 0.0
        Water_total = 0.0

    # WUE in L/kWh (≈ kg/kWh), consistent with your tower function
    if Power_IT > 0:
        WUE = Water_total * 3600.0 / Power_IT
    else:
        WUE = np.nan

    return (WUE,m_air,m_water,Water_evap,Water_drift,Water_blowdown,T_air_in_coil)

# (used for HDC_WE, Colo_WE)
def waterside_economizer(T_sfw,T_rfw,Twb_oa,AT_CT,AT_HE,Cooling_required):
    if (Twb_oa + AT_CT + AT_HE) <= T_sfw:
        use = 1
        WE_heat_removed = Cooling_required
    elif (Twb_oa + AT_CT + AT_HE) > T_sfw and (Twb_oa + AT_CT + AT_HE) < T_rfw:
        use = 1
        WE_heat_removed = Cooling_required*((T_rfw-(Twb_oa + AT_CT + AT_HE))/(T_rfw-T_sfw))
    else:
        use = 0
        WE_heat_removed = 0
    return use, WE_heat_removed
    
def waterside_economizer_drycooler(T_sfw, T_rfw, T_oa, AT_DC, AT_HE, Cooling_required):
    # This mirrors `waterside_economizer(...)` but uses outdoor dry-bulb for a dry cooler (instead of wet-bulb for a tower).
    # T_sfw: supply facility water temp to the load (CDU/coil) [°C]
    # T_rfw: return facility water temp from the load (CDU/coil) [°C]
    # T_oa: outdoor dry-bulb temperature [°C]
    # AT_DC: dry cooler approach temperature [°C]
    # AT_HE: economizer heat-exchanger approach temperature [°C]
    # Cooling_required: total cooling load to be removed at the load side [kW]
    if (T_oa + AT_DC + AT_HE) <= T_sfw:                                    # ambient + approaches can reach supply water setpoint
        use = 1                                                            # economizer is available
        WE_heat_removed = Cooling_required                                 # full free cooling covers the whole load [kW]
    elif (T_oa + AT_DC + AT_HE) > T_sfw and (T_oa + AT_DC + AT_HE) < T_rfw: # ambient allows partial free cooling between supply/return
        use = 1                                                            # economizer is partially available
        WE_heat_removed = Cooling_required * (                             # linear fraction between return and supply constraints
            (T_rfw - (T_oa + AT_DC + AT_HE)) / (T_rfw - T_sfw)
        )
    else:                                                                  # ambient + approaches is warmer than return water
        use = 0                                                            # economizer cannot run
        WE_heat_removed = 0                                                 # no free cooling [kW]
    return use, WE_heat_removed                                             # return (economizer_on, economizer_heat_removed_kW)


def _as_param_dict(w, param_order):
    # Utility: accept either dict inputs (recommended) or list/array inputs (legacy style like your existing functions).
    if isinstance(w, dict):                                                 # user passed a dict of named parameters
        return dict(w)                                                      # copy to avoid mutating the caller’s object
    w = np.asarray(w, dtype=float).ravel()                                  # user passed a numeric vector -> coerce to 1-D array
    if len(w) < len(param_order):                                           # validate the vector is long enough
        raise ValueError(f"w must have at least {len(param_order)} entries; got {len(w)}.")
    return {name: w[i] for i, name in enumerate(param_order)}               # map index -> parameter name

# -----------------------------
# Waste heat recovery utilities
# -----------------------------
def heat_pump_heating_cop(
    T_hot_supply_C: float,
    T_cold_source_C: float,
    eta_carnot: float = 0.45,
    dT_cond_C: float = 3.0,
    dT_evap_C: float = 3.0,
    cop_min: float = 1.5,
    cop_max: float = 12.0
) -> float:
    """Simple benchmark heat-pump COP model (heating mode).

    COP_heating ≈ eta_carnot * COP_Carnot, where COP_Carnot = T_hot / (T_hot - T_cold).

    Small approach allowances are applied for condenser/evaporator, and COP is bounded
    to avoid numerical blow-ups for near-zero lift.
    """
    Th = (float(T_hot_supply_C) + float(dT_cond_C)) + 273.15
    Tc = (float(T_cold_source_C) - float(dT_evap_C)) + 273.15

    Th = max(Th, Tc + 1.0)

    cop_carnot = Th / (Th - Tc)
    cop = float(eta_carnot) * float(cop_carnot)

    cop = max(float(cop_min), cop)
    cop = min(float(cop_max), cop)
    return cop


# (used for HDC_WE, Colo_WE)
def Chiller_system(T_up,T_lw,dp_up,dp_lw,RH_up,RH_lw,T_oa,RH_oa,P_oa,delta_T_air):
    # how to select temperature: can be changed to random select based on outdoor climate (linear)
    T_sa = np.mean([T_up,T_lw])
    #T_sa = np.random.uniform(T_up,T_lw,1)[0] 
    d_up = np.minimum(HAPropsSI('W','T',T_sa+273.15,'RH',RH_up/100,'P',P_oa),HAPropsSI('W','T',T_sa+273.15,'Tdp',dp_up+273.15,'P',P_oa))
    d_lw = np.maximum(HAPropsSI('W','T',T_sa+273.15,'RH',RH_lw/100,'P',P_oa),HAPropsSI('W','T',T_sa+273.15,'Tdp',dp_lw+273.15,'P',P_oa))
    # how to select absolute humidity
    d_sa = np.mean([d_up,d_lw])
    #d_sa = np.random.uniform(d_up,d_lw,1)[0]
    H_sa = HAPropsSI('H','T',T_sa+273.15,'P',P_oa,'W',d_sa)
    return T_sa,d_sa,H_sa




###############################
###### PUE&WUE functions ######
###############################

# PUE & WUE for Data Center with Airside Economizer (cooling-tower heat rejection)
def PUE_WUE_Aireconomizer(w):
    # Airside economizer + water-cooled chiller + cooling tower.
    # Input `w`: dict (recommended) or list/array following `param_order` below.
    param_order = [
        "T_oa",              # outdoor dry-bulb [°C]
        "RH_oa",             # outdoor relative humidity [%]
        "P_oa",              # outdoor pressure [Pa]
        "UPS_e",             # UPS efficiency [-]
        "PD_lr",             # power distribution loss ratio [-]
        "L_percentage",      # lighting fraction of IT power [-]
        "delta_T_air",       # supply-to-return air temperature rise [°C]
        "Fan_Pressure_CRAC", # CRAC/CRAH fan pressure rise [Pa]
        "Fan_e_CRAC",        # CRAC/CRAH fan efficiency [-]
        "Pump_Pressure_HD",  # humidification pump pressure rise [Pa]
        "Pump_e_HD",         # humidification pump efficiency [-]
        "AT_CT",             # cooling tower approach temperature [°C]
        "Chiller_load",      # chiller load indicator for GP COP model [-]
        "delta_T_water",     # chilled-water delta-T [°C]
        "Pump_Pressure_CW",  # chilled-water pump pressure rise [Pa]
        "Pump_e_CW",         # chilled-water pump efficiency [-]
        "Pump_Pressure_WHR",# waste heat reuse pump pressure rise [Pa]
        "Pump_e_WHR",      # waste heat reuse pump efficiency [-]    
        "delta_T_CT",        # cooling tower water delta-T [°C]
        "Pump_Pressure_CT",  # cooling tower pump pressure rise [Pa]
        "Pump_e_CT",         # cooling tower pump efficiency [-]
        "Windage_p",         # tower drift/windage fraction [-]
        "CC",                # tower cycles of concentration [-]
        "Fan_Pressure_CT",   # cooling tower fan pressure rise [Pa]
        "Fan_e_CT",          # cooling tower fan efficiency [-]
        "SHR",               # space sensible heat ratio [-]
        "LGRatio",           # L/G proxy used in Cooling_Tower [-]
        "T_up",              # upper bound supply air temperature [°C]
        "T_lw",              # lower bound supply air temperature [°C]
        "dp_up",             # upper bound dewpoint [°C]
        "dp_lw",             # lower bound dewpoint [°C]
        "RH_up",             # upper bound RH setpoint [%]
        "RH_lw",             # lower bound RH setpoint [%]
        "pcop",              # COP scaling factor [-]
        "HTE",               # Heat exchange (CRAH-water) effectiveness [-]
        "T_dh_supply",        # district heating required supply temperature [°C] 
        "T_dh_return",        # district heating return temperature [°C]
        "AT_HR_reuse",        # HX approach for heat recovery [°C]
        "eta_HR_reuse",       # heat recovery effectiveness factor [-]
        "HP_eta_carnot",      # Heating Pump Parameter
        "HP_dT_cond",         # Heating Pump Parameter
        "HP_dT_evap",         # Heating Pump Parameter
        "HP_cop_min",         # Heating Pump Parameter
        "HP_cop_max",         # Heating Pump Parameter      
        "HP_lift_max",
        "HP_T_source_min",
    ]
    p = _as_param_dict(w, param_order)                                      # normalize inputs into a dict `p[...]`

    Power_IT = 1.0                                                         # 1 kW IT basis (matches your current convention)
    w_eff = 1.0                                                            # humidification water efficiency (keep as 1.0 here)

    Fan_Power  = lambda m_dot, rho, dP, eta: (m_dot / rho) * dP / eta / 1000.0     # fan power [kW]
    Pump_Power = lambda m_dot, dP, eta, rho: dP * m_dot / (1000.0 * eta * rho)      # pump power [kW]

    UPS_loss   = (Power_IT / p["UPS_e"] - Power_IT)                        # UPS losses [kW]
    PD_loss    = (Power_IT / (1.0 - p["PD_lr"]) - Power_IT)                # power distribution losses [kW]
    Light_heat = Power_IT * p["L_percentage"]                              # lighting heat [kW]
    Q_base     = Power_IT + UPS_loss + PD_loss + Light_heat                # base heat to be removed [kW]

    # --- Air-side economizer psychrometrics (call once, reuse outputs) ---
    ae = Air_side_economizer(
        p["T_up"], p["T_lw"], p["dp_up"], p["dp_lw"], p["RH_up"], p["RH_lw"],
        p["T_oa"], p["RH_oa"], p["P_oa"], p["delta_T_air"]
    )
    AE_use  = ae[0]                                                        # 1 if air economizer is active
    HD_use  = ae[1]                                                        # 1 if adiabatic humidification is active
    delta_d = ae[4]                                                        # absolute humidity increase needed [kg/kg_da]
    T_sa    = ae[5]                                                        # supply air temperature [°C]
    H_sa    = ae[6] / 1000.0                                               # supply air enthalpy [kJ/kg_da]
    H_cd    = ae[8] / 1000.0                                               # conditioned-air enthalpy [kJ/kg_da]
    d_sa    = ae[9]                                                        # supply air humidity ratio [kg_w/kg_da]

    T_ra = T_sa + p["delta_T_air"]                                         # return air temperature [°C]
    H_ra = H_sa + 1.01 * p["delta_T_air"]                                  # return air enthalpy [kJ/kg_da] (cp_air ≈ 1.01)
    
    # Facility water temperatures (legacy HTE closure)
    T_sfw = T_ra - (T_ra - T_sa) / p["HTE"]                                 # supply facility water [°C]
    T_rfw = T_sfw + p["delta_T_water"]                                      # return facility water [°C]

    # Air mass flow rate needed to remove the facility heat (kW = kJ/s)
    m_sa = Q_base / max(H_ra - H_sa, 1e-12)                                # supply air mass flow [kg/s]
    m_cd = m_sa * (H_sa - H_ra) / max(H_cd - H_ra, -1e-9)                  # conditioned-air mass flow [kg/s]

    # Convert to dry-air basis for humidification accounting
    m_cd_dry = m_cd / (1.0 + d_sa)      

    # --- Middle-phase air-side economizer: modulate outdoor-air fraction (damper control) ---
    # Optional dict inputs (do not affect legacy vector inputs):
    x_oa_min = float(p.get("x_oa_min", 0.10))                               # minimum outdoor-air fraction [-]
    x_oa_max = float(p.get("x_oa_max", 1.00))                               # maximum outdoor-air fraction [-]
    x_oa_min = np.clip(x_oa_min, 0.0, 1.0)
    x_oa_max = np.clip(x_oa_max, x_oa_min, 1.0)

    # Outdoor-air enthalpy on dry-air basis [kJ/kg_da]
    H_oa = HAPropsSI('H', 'T', p["T_oa"] + 273.15, 'P', p["P_oa"], 'RH', p["RH_oa"] / 100.0) / 1000.0

    # Target is the supply-air enthalpy (coil outlet); damper chooses x_oa to reduce coil load
    H_target = H_sa

    if H_oa < H_ra - 1e-9:
        # fraction that would (ideally) bring mixed air to H_target without mechanical cooling
        denom = (H_oa - H_ra)
        x_need = (H_target - H_ra) / denom if abs(denom) > 1e-12 else x_oa_min
        x_oa = float(np.clip(x_need, x_oa_min, x_oa_max))
    else:
        x_oa = x_oa_min

    AE_use = 1 if x_oa > x_oa_min + 1e-6 else 0                            # keep legacy flag for reporting

    # Mixed-air enthalpy (baseline at x_oa_min, actual at x_oa) [kJ/kg_da]
    H_mix_base = x_oa_min * H_oa + (1.0 - x_oa_min) * H_ra
    H_mix      = x_oa     * H_oa + (1.0 - x_oa)     * H_ra

    # Coil (mechanical) cooling load [kW]; economizer "benefit" is coil-load reduction vs baseline minimum OA
    Coil_load_base = m_sa * max(H_mix_base - H_sa, 0.0)                    # [kW]
    Coil_load      = m_sa * max(H_mix      - H_sa, 0.0)                    # [kW]
    Q_AE           = max(Coil_load_base - Coil_load, 0.0)                  # [kW] (reported economizer contribution)
    
    # Supply air density (moist air)
    rho_sa = 1.0 / HAPropsSI('Vha', 'T', T_sa + 273.15, 'W', d_sa, 'P', p["P_oa"])  # [kg/m3]

    # CRAC/CRAH fan power
    Power_Fan_CRAC = Fan_Power(m_sa, rho_sa, p["Fan_Pressure_CRAC"], p["Fan_e_CRAC"])  # [kW]

    # Adiabatic humidification water (air economizer mode)
    Water_HD_AE = max(HD_use * m_cd_dry * delta_d, 0.0)                    # [kg_w/s]

    # Remaining load for the waste heat reuse and chiller
    Remain_sensible = max(Q_base - Q_AE, 0.0)                             # [kW]

    # Add latent portion when the chiller is active (consistent with your original implementation)
    if Remain_sensible > 0:
        Q_latent = Remain_sensible / p["SHR"] - Remain_sensible          # [kW]
        Remain_heat_removed = Remain_sensible + max(Q_latent, 0.0)       # [kW]
        d_ra_remain = max(Q_latent, 0.0) / 2266.0                         # [kg_w/kg_da] proxy via latent heat (kJ/kg)
        Water_HD = max(d_ra_remain, 0.0)                                  # humidification water proxy [kg/s] (legacy convention)
    else:
        Remain_heat_removed = 0.0
        Water_HD = 0.0

    # Humidification pump power
    Power_Pump_HD = Pump_Power(Water_HD, p["Pump_Pressure_HD"], p["Pump_e_HD"], 1000.0)  # [kW]

    # Outdoor wet-bulb and density (for tower & COP proxy)
    Twb_oa = HAPropsSI('Twb', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"] / 100.0, 'P', p["P_oa"]) - 273.15  # [°C]
    rho_oa = 1.0 / HAPropsSI('Vha', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"] / 100.0, 'P', p["P_oa"])     # [kg/m3]
    
    #waste heat reuse branch
    T_sup = float(p.get("T_dh_supply", 60.0))
    T_ret = float(p.get("T_dh_return", 30.0))
    AT_HR = float(p.get("AT_HR_reuse", 3.0))
    eta_HR = float(p.get("eta_HR_reuse", 0.90))
    cp_water = 4.184                                                       # water cp [kJ/kg-K] consistent with your model

    # Heat pump operating constraints / guards (optional)
    dT_lift_max = float(p.get("HP_lift_max", 0.35))
    T_source_min = float(p.get("HP_T_source_min", -5.0))

    # Source-side effective hot temperature after HX approach
    T_heff = float(T_rfw) - AT_HR

    # Direct recovery fraction (0..1) based on DH return/supply span
    if T_sup <= T_ret:
        # fallback: treat as single-point requirement
        frac_direct = 1.0 if T_heff >= T_sup else 0.0
    else:
        if T_heff >= T_sup:
            frac_direct = 1.0
        elif T_heff <= T_ret:
            frac_direct = 0.0
        else:
            frac_direct = (T_heff - T_ret) / (T_sup - T_ret)

    Q_source = float(Remain_heat_removed)
    Q_direct_recovered = max(0.0, eta_HR * frac_direct * Q_source)

    # Remaining waste heat potentially available to a heat pump (as evaporator heat input)
    if (T_heff >= T_source_min):
        Q_hp_in = max(0.0, eta_HR * (1.0 - frac_direct) * Q_source)
    else:
        Q_hp_in = 0
    P_hp = 0.0
    Q_hp_delivered = 0.0

    if (T_heff >= T_source_min) and Q_hp_in > 0:
        cop = heat_pump_heating_cop(
            T_hot_supply_C=T_sup,
            T_cold_source_C=T_heff,
            eta_carnot=float(p.get("HP_eta_carnot", 0.45)),
            dT_cond_C=float(p.get("HP_dT_cond", 3.0)),
            dT_evap_C=float(p.get("HP_dT_evap", 3.0)),
            cop_min=float(p.get("HP_cop_min", 1.5)),
            cop_max=float(p.get("HP_cop_max", 12.0)),
        )
        if cop > 1.01:
            # Heating-mode energy balance:
            #   Q_out = Q_in + P, with COP = Q_out / P
            # => Q_out = Q_in * COP/(COP-1);  P = Q_in/(COP-1)
            Q_hp_delivered = Q_hp_in * cop / (cop - 1.0)
            # No heat reuse if exceed the max lift capacity
            if (Q_hp_delivered-Q_hp_in)/Q_hp_in > dT_lift_max:
                Q_hp_delivered = 0.0
                Q_hp_in = 0.0
            P_hp = Q_hp_in / (cop - 1.0)
        else:
            Q_hp_in = 0
            
    
    results = {}
    cases = [
        ("base",   Remain_heat_removed,                    0.0),
        ("whr",    Remain_heat_removed - Q_direct_recovered, 0.0),
        ("whr_hp", Remain_heat_removed - Q_direct_recovered - Q_hp_in, P_hp)
    ]
    for name, CoolingRequired, extra_power in cases:
        m_whrw = (Remain_heat_removed - CoolingRequired) / (cp_water * p["delta_T_water"])              # waste heat-handled facility water mass flow [kg/s]
        Power_Pump_WHR = Pump_Power(m_whrw, p["Pump_Pressure_WHR"], p["Pump_e_WHR"], 1000.0)             # WE pump power [kW]
        # Chiller COP (water-cooled GP surrogate)
        if CoolingRequired > 0:
            COP_chiller = COP_gp.predict(
                np.array([Twb_oa + p["AT_CT"], p["Chiller_load"]]).reshape(1, 2)
            )[0] * (1.0 + p["pcop"])
            COP_chiller = max(float(COP_chiller), 0.1)                         # avoid non-physical COP
            Power_Chiller = CoolingRequired / COP_chiller                 # [kW]
        else:
            Power_Chiller = 0.0

        # Chilled-water loop
        m_sw = CoolingRequired / (cp_water * max(p["delta_T_water"], 1e-9))  # [kg/s]
        Power_Pump_CW = Pump_Power(m_sw, p["Pump_Pressure_CW"], p["Pump_e_CW"], 1000.0)  # [kW]

        # Heat rejected to the cooling tower (matches your existing Aireconomizer convention)
        Hrej = CoolingRequired + Power_Chiller                    # [kW]

        m_CT = Hrej / (cp_water * max(p["delta_T_CT"], 1e-9))
        Power_Pump_CT = Pump_Power(m_CT, p["Pump_Pressure_CT"], p["Pump_e_CT"], 1000.0)

        _WUE_CT, m_CT_air, _mratio, Water_evap, Water_windage, Water_DF = Cooling_Tower(
            p["T_oa"], p["RH_oa"], p["P_oa"], p["AT_CT"], Power_IT, Hrej,
            p["delta_T_CT"], p["Windage_p"], p["CC"], p["LGRatio"]
        )
        
        Power_Fan_CT = Fan_Power(m_CT_air, rho_oa, p["Fan_Pressure_CT"], p["Fan_e_CT"])   # [kW]

        Power_comp = np.array([
            Power_IT, UPS_loss, PD_loss, Light_heat, Power_Fan_CRAC,
            Power_Pump_WHR, Power_Pump_HD, Power_Chiller, Power_Pump_CW,
            Power_Pump_CT, Power_Fan_CT, extra_power
        ])
        
        Water_reject_kgps = max(Water_evap, 0.0) + max(Water_windage, 0.0) + max(Water_DF, 0.0)
        Water_total_kgps = Water_HD / w_eff + Water_reject_kgps

        PUE = np.sum(Power_comp) / Power_IT
        WUE = Water_total_kgps * 3600.0 / Power_IT

        results[name] = (PUE, WUE)

    PUE, WUE = results["base"]
    PUE_whr, WUE_whr = results["whr"]
    PUE_whr_hp, WUE_whr_hp = results["whr_hp"]

    return PUE, WUE, PUE_whr, WUE_whr, PUE_whr_hp, WUE_whr_hp, Q_direct_recovered, Q_hp_in, Q_hp_delivered, P_hp

def PUE_WUE_CoolingTower_Aireconomizer(w):
    # Explicit-name wrapper for: airside economizer + cooling tower heat rejection.
    return PUE_WUE_Aireconomizer(w)


# PUE & WUE for Data Center with Waterside Economizer (cooling-tower heat rejection)
def PUE_WUE_Watereconomizer(w):
    # Waterside economizer + water-cooled chiller + cooling tower.
    # Input `w`: dict (recommended) or list/array following `param_order` below.
    param_order = [
        "T_oa",               # outdoor dry-bulb [°C]
        "RH_oa",              # outdoor relative humidity [%]
        "P_oa",               # outdoor pressure [Pa]
        "UPS_e",              # UPS efficiency [-]
        "PD_lr",              # power distribution loss ratio [-]
        "L_percentage",       # lighting fraction of IT power [-]
        "delta_T_air",        # supply-to-return air temperature rise [°C]
        "Fan_Pressure_CRAC",  # CRAC/CRAH fan pressure rise [Pa]
        "Fan_e_CRAC",         # CRAC/CRAH fan efficiency [-]
        "Pump_Pressure_HD",   # humidification pump pressure rise [Pa]
        "Pump_e_HD",          # humidification pump efficiency [-]
        "AT_CT",              # cooling tower approach temperature [°C]
        "Chiller_load",       # chiller load indicator for GP COP model [-]
        "delta_T_water",      # facility/chilled-water delta-T [°C]
        "Pump_Pressure_CW",   # chilled-water pump pressure rise [Pa]
        "Pump_e_CW",          # chilled-water pump efficiency [-]
        "delta_T_CT",         # cooling tower water delta-T [°C]
        "Pump_Pressure_CT",   # cooling tower pump pressure rise [Pa]
        "Pump_e_CT",          # cooling tower pump efficiency [-]
        "Windage_p",          # tower drift/windage fraction [-]
        "CC",                 # tower cycles of concentration [-]
        "Fan_Pressure_CT",    # cooling tower fan pressure rise [Pa]
        "Fan_e_CT",           # cooling tower fan efficiency [-]
        "SHR",                # space sensible heat ratio [-]
        "LGRatio",            # L/G proxy used in Cooling_Tower [-]
        "T_up",               # upper bound supply air temperature [°C]
        "T_lw",               # lower bound supply air temperature [°C]
        "dp_up",              # upper bound dewpoint [°C]
        "dp_lw",              # lower bound dewpoint [°C]
        "RH_up",              # upper bound RH setpoint [%]
        "RH_lw",              # lower bound RH setpoint [%]
        "pcop",               # COP scaling factor [-]
        "HTE",                # heat-transfer effectiveness (air-to-water coil / CRAH) [-]
        "AT_HE",              # waterside economizer heat-exchanger approach [°C]
        "Pump_Pressure_WHR",# waste heat reuse pump pressure rise [Pa]
        "Pump_e_WHR",      # waste heat reuse pump efficiency [-]    
        "Pump_Pressure_WE",   # waterside economizer pump pressure rise [Pa]
        "Pump_e_WE",          # waterside economizer pump efficiency [-]
        "T_dh_supply",        # district heating required supply temperature [°C] 
        "T_dh_return",        # district heating return temperature [°C]
        "AT_HR_reuse",        # HX approach for heat recovery [°C]
        "eta_HR_reuse",       # heat recovery effectiveness factor [-]
        "HP_eta_carnot",      # Heating Pump Parameter
        "HP_dT_cond",         # Heating Pump Parameter
        "HP_dT_evap",         # Heating Pump Parameter
        "HP_cop_min",         # Heating Pump Parameter
        "HP_cop_max",         # Heating Pump Parameter      
        "HP_lift_max",
        "HP_T_source_min",
    ]
    p = _as_param_dict(w, param_order)                                      # normalize inputs into a dict `p[...]`

    Power_IT = 1.0                                                         # 1 kW IT basis
    w_eff = 1.0                                                            # humidification water efficiency (keep as 1.0 here)

    Fan_Power  = lambda m_dot, rho, dP, eta: (m_dot / rho) * dP / eta / 1000.0     # fan power [kW]
    Pump_Power = lambda m_dot, dP, eta, rho: dP * m_dot / (1000.0 * eta * rho)      # pump power [kW]

    UPS_loss   = (Power_IT / p["UPS_e"] - Power_IT)                        # UPS losses [kW]
    PD_loss    = (Power_IT / (1.0 - p["PD_lr"]) - Power_IT)                # power distribution losses [kW]
    Light_heat = Power_IT * p["L_percentage"]                              # lighting heat [kW]
    Q_base     = Power_IT + UPS_loss + PD_loss + Light_heat                # base sensible heat [kW]

    # Outdoor wet-bulb and density (economizer and tower)
    Twb_oa = HAPropsSI('Twb', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"] / 100.0, 'P', p["P_oa"]) - 273.15  # [°C]
    rho_oa = 1.0 / HAPropsSI('Vha', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"] / 100.0, 'P', p["P_oa"])     # [kg/m3]

    # Latent load fraction (same convention as your legacy function)
    Q_latent = Q_base / p["SHR"] - Q_base                                   # [kW]
    Cooling_required = Q_base + max(Q_latent, 0.0)                          # total cooling duty [kW]

    # Choose indoor supply air state (legacy: random draw inside bounds)
    cs = Chiller_system(
        p["T_up"], p["T_lw"], p["dp_up"], p["dp_lw"], p["RH_up"], p["RH_lw"],
        p["T_oa"], p["RH_oa"], p["P_oa"], p["delta_T_air"]
    )
    T_sa, d_sa, H_sa = cs[0], cs[1], cs[2] / 1000.0                         # [°C], [kg/kg_da], [kJ/kg_da]
    T_ra = T_sa + p["delta_T_air"]                                          # [°C]

    # Air mass flow sized on sensible load (kW = kJ/s)
    m_sa = Q_base / (1.01 * max(p["delta_T_air"], 1e-9))                    # [kg/s]
    rho_sa = 1.0 / HAPropsSI('Vha', 'T', T_sa + 273.15, 'W', d_sa, 'P', p["P_oa"])  # [kg/m3]
    Power_Fan_CRAC = Fan_Power(m_sa, rho_sa, p["Fan_Pressure_CRAC"], p["Fan_e_CRAC"])  # [kW]

    # Humidification water proxy and pump power (legacy convention)
    Water_HD = max(Q_latent, 0.0) / 2266.0                                  # [kg/s]
    Power_Pump_HD = Pump_Power(Water_HD, p["Pump_Pressure_HD"], p["Pump_e_HD"], 1000.0)  # [kW]

    # Facility water temperatures (legacy HTE closure)
    T_sfw = T_ra - (T_ra - T_sa) / p["HTE"]                                 # supply facility water [°C]
    T_rfw = T_sfw + p["delta_T_water"]                                      # return facility water [°C]
    

    #waste heat reuse branch
    # --- Waste heat reuse (district heating) ---
    T_sup = float(p.get("T_dh_supply", 60.0))
    T_ret = float(p.get("T_dh_return", 30.0))
    AT_HR = float(p.get("AT_HR_reuse", 3.0))
    eta_HR = float(p.get("eta_HR_reuse", 0.90))

    # Heat pump operating constraints / guards (optional)
    dT_lift_max = float(p.get("HP_lift_max", 0.35))
    T_source_min = float(p.get("HP_T_source_min", -5.0))

    # Source-side effective hot temperature after HX approach
    T_heff = float(T_rfw) - AT_HR

    # Direct recovery fraction (0..1) based on DH return/supply span
    if T_sup <= T_ret:
        # fallback: treat as single-point requirement
        frac_direct = 1.0 if T_heff >= T_sup else 0.0
    else:
        if T_heff >= T_sup:
            frac_direct = 1.0
        elif T_heff <= T_ret:
            frac_direct = 0.0
        else:
            frac_direct = (T_heff - T_ret) / (T_sup - T_ret)

    Q_source = float(Cooling_required)
    Q_direct_recovered = max(0.0, eta_HR * frac_direct * Q_source)

    # Remaining waste heat potentially available to a heat pump (as evaporator heat input)
    if (T_heff >= T_source_min):
        Q_hp_in = max(0.0, eta_HR * (1.0 - frac_direct) * Q_source)
    else:
        Q_hp_in = 0
    P_hp = 0.0
    Q_hp_delivered = 0.0

    if (T_heff >= T_source_min) and Q_hp_in > 0:
        cop = heat_pump_heating_cop(
            T_hot_supply_C=T_sup,
            T_cold_source_C=T_heff,
            eta_carnot=float(p.get("HP_eta_carnot", 0.45)),
            dT_cond_C=float(p.get("HP_dT_cond", 3.0)),
            dT_evap_C=float(p.get("HP_dT_evap", 3.0)),
            cop_min=float(p.get("HP_cop_min", 1.5)),
            cop_max=float(p.get("HP_cop_max", 12.0)),
        )
        if cop > 1.01:
            # Heating-mode energy balance:
            #   Q_out = Q_in + P, with COP = Q_out / P
            # => Q_out = Q_in * COP/(COP-1);  P = Q_in/(COP-1)
            Q_hp_delivered = Q_hp_in * cop / (cop - 1.0)
            # No heat reuse if exceed the max lift capacity
            if (Q_hp_delivered-Q_hp_in)/Q_hp_in > dT_lift_max:
                Q_hp_delivered = 0.0
                Q_hp_in = 0.0
            P_hp = Q_hp_in / (cop - 1.0)
        else:
            Q_hp_in = 0
    
    # water-side economizer & Chiller branch  
    Twb_oa = HAPropsSI('Twb', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"]/100.0, 'P', p["P_oa"]) - 273.15  # wet-bulb [°C]
    rho_oa = 1.0 / HAPropsSI('Vha', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"]/100.0, 'P', p["P_oa"])     # moist-air density [kg/m3]
    
    cp_water = 4.184                                                       # water cp [kJ/kg-K] consistent with your model
    
    results = {}
    cases = [
        ("base",   Cooling_required,                    0.0),
        ("whr",    Cooling_required - Q_direct_recovered, 0.0),
        ("whr_hp", Cooling_required - Q_direct_recovered - Q_hp_in, P_hp)
    ]
    for name, CoolingRequired, extra_power in cases:
        m_whrw = (Cooling_required - CoolingRequired) / (cp_water * p["delta_T_water"])              # waste heat-handled facility water mass flow [kg/s]
        Power_Pump_WHR = Pump_Power(m_whrw, p["Pump_Pressure_WHR"], p["Pump_e_WHR"], 1000.0)             # WE pump power [kW]
        
        # Waterside economizer availability (wet-bulb constrained for cooling tower)
        WE_use, WE_heat_removed = waterside_economizer(
            T_sfw, T_rfw, Twb_oa, p["AT_CT"], p["AT_HE"], CoolingRequired
        )


        m_sfw = CoolingRequired / (cp_water * p["delta_T_water"])              # economizer-handled facility water mass flow [kg/s]
        Power_Pump_WE = Pump_Power(m_sfw, p["Pump_Pressure_WE"], p["Pump_e_WE"], 1000.0)  # WE pump power [kW]

        Chiller_heat_removed = CoolingRequired - WE_heat_removed              # remaining cooling duty for chiller [kW]

        m_sw = Chiller_heat_removed / (cp_water * p["delta_T_water"])          # chilled water mass flow [kg/s]
        Power_Pump_CW = Pump_Power(m_sw, p["Pump_Pressure_CW"], p["Pump_e_CW"], 1000.0)  # chilled water pump power [kW]

        if Chiller_heat_removed > 0:                                           # only compute chiller power when needed
            COP_chiller = COP_gp.predict(                                  # GP COP: input is (condenser entering temp proxy, load)
                np.array([Twb_oa + p["AT_CT"], p["Chiller_load"]]).reshape(1, 2)
            )[0] * (1.0 + p["pcop"])
            COP_chiller = max(float(COP_chiller), 0.1)                         # clip to avoid non-physical COP due to extrapolation
            Power_Chiller = Chiller_heat_removed / COP_chiller                 # chiller electrical power [kW]
        else:                                                                  # if economizer fully covers the load
            Power_Chiller = 0.0                                                # no chiller power

        Hrej = CoolingRequired + Power_Chiller

        _WUE_CT, m_CT_air, _mratio, Water_evap, Water_windage, Water_DF = Cooling_Tower(
            p["T_oa"], p["RH_oa"], p["P_oa"], p["AT_CT"], Power_IT, Hrej,
            p["delta_T_CT"], p["Windage_p"], p["CC"], p["LGRatio"]
        )
        
        Power_Fan_CT = Fan_Power(m_CT_air, rho_oa, p["Fan_Pressure_CT"], p["Fan_e_CT"])   # [kW]

        Power_comp = np.array([
            Power_IT, UPS_loss, PD_loss, Light_heat, Power_Fan_CRAC,
            Power_Pump_HD, Power_Pump_WE, Power_Chiller, Power_Pump_CW,
            Power_Pump_WHR, Power_Fan_CT, extra_power
        ])

        Water_reject_kgps = max(Water_evap, 0.0) + max(Water_windage, 0.0) + max(Water_DF, 0.0)
        Water_total_kgps = Water_HD / w_eff + Water_reject_kgps

        PUE = np.sum(Power_comp) / Power_IT
        WUE = Water_total_kgps * 3600.0 / Power_IT

        results[name] = (PUE, WUE)

    PUE, WUE = results["base"]
    PUE_whr, WUE_whr = results["whr"]
    PUE_whr_hp, WUE_whr_hp = results["whr_hp"]
    return PUE, WUE, PUE_whr, WUE_whr, PUE_whr_hp, WUE_whr_hp, Q_direct_recovered, Q_hp_in, Q_hp_delivered, P_hp

def PUE_WUE_CoolingTower_Watereconomizer(w):
    # Explicit-name wrapper for: waterside economizer + cooling tower heat rejection.
    return PUE_WUE_Watereconomizer(w)


def _PUE_WUE_liquid_watereconomizer_core(w, rejection_type):
    # Core model for: liquid cooling (DTC or immersion) + waterside economizer + (dry cooler OR cooling tower) heat rejection.
    # Depends on your existing definitions: HAPropsSI, waterside_economizer, Cooling_Tower, Dry_Cooler, COP_gp, COP_air_gp.
    # rejection_type: "drycooler" or "coolingtower".
    param_order = [                                                         # if w is a list/array, it must follow THIS exact ordering
        "T_oa",            # outdoor dry-bulb [°C]
        "RH_oa",           # outdoor relative humidity [%]
        "P_oa",            # outdoor pressure [Pa]
        "UPS_e",           # UPS efficiency [-]
        "PD_lr",           # power distribution loss ratio [-]
        "L_percentage",    # lighting fraction of IT power [-]
        "Cooling_required_factor",  # optional multiplier for base heat load (use 1.0 if not needed) [-]
        "f_liquid",        # fraction of total load captured by liquid loop [-]
        "T_it_supply",     # IT coolant supply temperature setpoint [°C]
        "delta_T_it",      # IT coolant temperature rise across servers [°C]
        "cp_it",           # IT coolant cp [kJ/kg-K]
        "rho_it",          # IT coolant density [kg/m3]
        "Pump_Pressure_IT",# IT coolant pump pressure rise [Pa]
        "Pump_e_IT",       # IT coolant pump efficiency [-]
        "AT_CDU",          # CDU (liquid-to-liquid HX) approach (facility water -> IT coolant) [°C]
        "delta_T_water",   # facility/chilled water delta-T at the load (CDU) [°C]
        "AT_HE",           # waterside economizer heat-exchanger approach [°C]
        "Pump_Pressure_WE",# economizer loop pump pressure rise [Pa]
        "Pump_e_WE",       # economizer loop pump efficiency [-]
        "Chiller_load",    # chiller load indicator for GP COP model [-]
        "pcop",            # COP scaling factor (e.g., degradation margin) [-]
        "Pump_Pressure_CW",# chilled water pump pressure rise [Pa]
        "Pump_e_CW",       # chilled water pump efficiency [-]
        "Fan_Pressure_room",# room/CRAH fan pressure rise [Pa] (used only if residual air load exists)
        "Fan_e_room",      # room/CRAH fan efficiency [-]
        "delta_T_air",# air delta-T for residual room load calculation [°C]
        # --- Dry cooler specific parameters (used if rejection_type == "drycooler") ---
        "AT_DC",           # dry cooler approach temperature [°C]
        "delta_T_DC_water",# condenser (dry cooler loop) water delta-T [°C]
        "epsilon_DC",      # coil effectiveness-like parameter in Dry_Cooler closure [-]
        "adiabatic_DC",    # 0/1 flag: adiabatic pre-cooling enabled (water consuming) [-]
        "eta_ad_DC",       # adiabatic saturation effectiveness [-]
        "drift_p_DC",      # drift fraction for adiabatic section [-]
        "CC_DC",           # cycles of concentration for adiabatic blowdown [-]
        "Fan_Pressure_DC", # dry cooler fan pressure rise [Pa]
        "Fan_e_DC",        # dry cooler fan efficiency [-]
        "Pump_Pressure_DC",# dry cooler loop pump pressure rise [Pa]
        "Pump_e_DC",       # dry cooler loop pump efficiency [-]
        # --- Cooling tower specific parameters (used if rejection_type == "coolingtower") ---
        "AT_CT",           # cooling tower approach temperature [°C]
        "delta_T_CT",      # cooling tower water delta-T [°C]
        "Windage_p_CT",    # tower drift/windage fraction [-]
        "CC_CT",           # tower cycles of concentration [-]
        "LGRatio_CT",      # L/G proxy used by your Cooling_Tower function [-]
        "Fan_Pressure_CT", # cooling tower fan pressure rise [Pa]
        "Fan_e_CT",        # cooling tower fan efficiency [-]
        "Pump_Pressure_CT",# cooling tower pump pressure rise [Pa]
        "Pump_e_CT",      # cooling tower pump efficiency [-]
        "Pump_Pressure_WHR",# waste heat reuse pump pressure rise [Pa]
        "Pump_e_WHR",      # waste heat reuse pump efficiency [-]        
        "T_dh_supply",        # district heating required supply temperature [°C] 
        "T_dh_return",        # district heating return temperature [°C]
        "AT_HR_reuse",        # HX approach for heat recovery [°C]
        "eta_HR_reuse",       # heat recovery effectiveness factor [-]
        "HP_eta_carnot",      # Heating Pump Parameter
        "HP_dT_cond",         # Heating Pump Parameter
        "HP_dT_evap",         # Heating Pump Parameter
        "HP_cop_min",         # Heating Pump Parameter
        "HP_cop_max",         # Heating Pump Parameter      
        "HP_lift_max",
        "HP_T_source_min",
    ]                                                                      # end param_order list
    p = _as_param_dict(w, param_order)                                     # normalize inputs into a dict `p[...]`

    Power_IT = 1.0                                                         # 1 kW IT basis (matches your current PUE/WUE convention)
    
    Twb_oa = HAPropsSI('Twb', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"]/100.0, 'P', p["P_oa"]) - 273.15  # wet-bulb [°C]
    rho_oa = 1.0 / HAPropsSI('Vha', 'T', p["T_oa"] + 273.15, 'RH', p["RH_oa"]/100.0, 'P', p["P_oa"])     # moist-air density [kg/m3]
    cp_water = 4.184                                                       # water cp [kJ/kg-K] consistent with your model

    Fan_Power = lambda m_dot, rho, dP, eta: (m_dot / rho) * dP / eta / 1000.0  # fan power [kW] from mass flow [kg/s]
    Pump_Power = lambda m_dot, dP, eta, rho: dP * m_dot / (1000.0 * eta * rho) # pump power [kW] from mass flow [kg/s]

    UPS_loss   = (Power_IT / p["UPS_e"] - Power_IT)                        # UPS losses [kW]
    PD_loss    = (Power_IT / (1.0 - p["PD_lr"]) - Power_IT)                # power distribution losses [kW]
    Light_heat = Power_IT * p["L_percentage"]                              # lighting heat [kW]
    Q_base     = Power_IT + UPS_loss + PD_loss + Light_heat                # base building heat to reject [kW]
    Cooling_required = Q_base * p["Cooling_required_factor"]               # optional scaling for additional internal loads [kW]

    Q_liquid = Cooling_required * p["f_liquid"]                            # heat captured by liquid cooling loop [kW]
    Q_air    = Cooling_required - Q_liquid                                 # residual heat left for room air system [kW]
    
    if Q_air > 0:
        m_air_room = Q_air / (1.01 * p["delta_T_air"])
        Power_Fan_room = Fan_Power(m_air_room, rho_oa, p["Fan_Pressure_room"], p["Fan_e_room"])
    else:
        Power_Fan_room = 0.0

    Power_Pump_IT = 0.0
    m_it = 0.0

    _it_pump_keys = ("delta_T_it", "Pump_Pressure_IT", "Pump_e_IT")
    _has_it_pump_inputs = all((k in p) and (p[k] is not None) for k in _it_pump_keys)

    if _has_it_pump_inputs and (Q_liquid > 0):
        if p["delta_T_it"] <= 0:
            raise ValueError("delta_T_it must be > 0 [°C] when IT pump inputs are provided.")
        if p["Pump_e_IT"] <= 0:
            raise ValueError("Pump_e_IT must be > 0 [-] when IT pump inputs are provided.")
        m_it = Q_liquid / (p["cp_it"] * p["delta_T_it"])  # [kg/s] (kW = kJ/s)
        Power_Pump_IT = Pump_Power(m_it, p["Pump_Pressure_IT"], p["Pump_e_IT"], p["rho_it"])  # [kW]

    T_sfw = p["T_it_supply"] - p["AT_CDU"]                                 # facility water supply temperature to CDU [°C]
    if p["delta_T_water"] <= 0:                                            # sanity check for facility water delta-T
        raise ValueError("delta_T_water must be > 0 [°C].")                # stop if invalid
    T_rfw = T_sfw + p["delta_T_water"]                                     # facility water return temperature from CDU [°C]
    
    #waste heat reuse branch
    # --- Waste heat reuse (district heating) ---
    T_sup = float(p.get("T_dh_supply", 60.0))
    T_ret = float(p.get("T_dh_return", 30.0))
    AT_HR = float(p.get("AT_HR_reuse", 3.0))
    eta_HR = float(p.get("eta_HR_reuse", 0.90))

    # Heat pump operating constraints / guards (optional)
    dT_lift_max = float(p.get("HP_lift_max", 0.35))
    T_source_min = float(p.get("HP_T_source_min", -5.0))

    # Source-side effective hot temperature after HX approach
    T_heff = float(T_rfw) - AT_HR
    

    # Direct recovery fraction (0..1) based on DH return/supply span
    if T_sup <= T_ret:
        # fallback: treat as single-point requirement
        frac_direct = 1.0 if T_heff >= T_sup else 0.0
    else:
        if T_heff >= T_sup:
            frac_direct = 1.0
        elif T_heff <= T_ret:
            frac_direct = 0.0
        else:
            frac_direct = (T_heff - T_ret) / (T_sup - T_ret)

    Q_source = float(Cooling_required)
    Q_direct_recovered = max(0.0, eta_HR * frac_direct * Q_source)

    # Remaining waste heat potentially available to a heat pump (as evaporator heat input)
    if (T_heff >= T_source_min):
        Q_hp_in = max(0.0, eta_HR * (1.0 - frac_direct) * Q_source)
    else:
        Q_hp_in = 0
    P_hp = 0.0
    Q_hp_delivered = 0.0

    if (T_heff >= T_source_min) and Q_hp_in > 0:
        cop = heat_pump_heating_cop(
            T_hot_supply_C=T_sup,
            T_cold_source_C=T_heff,
            eta_carnot=float(p.get("HP_eta_carnot", 0.45)),
            dT_cond_C=float(p.get("HP_dT_cond", 3.0)),
            dT_evap_C=float(p.get("HP_dT_evap", 3.0)),
            cop_min=float(p.get("HP_cop_min", 1.5)),
            cop_max=float(p.get("HP_cop_max", 12.0)),
        )
        if cop > 1.01:
            # Heating-mode energy balance:
            #   Q_out = Q_in + P, with COP = Q_out / P
            # => Q_out = Q_in * COP/(COP-1);  P = Q_in/(COP-1)
            Q_hp_delivered = Q_hp_in * cop / (cop - 1.0)
            # No heat reuse if exceed the max lift capacity
            if (Q_hp_delivered-Q_hp_in)/Q_hp_in > dT_lift_max:
                Q_hp_delivered = 0.0
                Q_hp_in = 0.0
            P_hp = Q_hp_in / (cop - 1.0)
        else:
            Q_hp_in = 0
    
    # water-side economizer & Chiller branch  
    results = {}
    cases = [
        ("base",   Cooling_required,                    0.0),
        ("whr",    Cooling_required - Q_direct_recovered, 0.0),
        ("whr_hp", Cooling_required - Q_direct_recovered - Q_hp_in, P_hp)
    ]
    for name, CoolingRequired, extra_power in cases:
        m_whrw = (Cooling_required - CoolingRequired) / (cp_water * p["delta_T_water"])              # waste heat-handled facility water mass flow [kg/s]
        Power_Pump_WHR = Pump_Power(m_whrw, p["Pump_Pressure_WHR"], p["Pump_e_WHR"], 1000.0)             # WE pump power [kW]
        if rejection_type == "coolingtower":                                   # tower case: economizer constrained by wet-bulb
            WE_use, WE_heat_removed = waterside_economizer(                    # call your existing WE function
                T_sfw, T_rfw, Twb_oa, p["AT_CT"], p["AT_HE"], CoolingRequired
            )
        elif rejection_type == "drycooler":                                    # dry cooler case: economizer constrained by dry-bulb
            WE_use, WE_heat_removed = waterside_economizer_drycooler(          # call the dry-bulb WE analog
                T_sfw, T_rfw, p["T_oa"], p["AT_DC"], p["AT_HE"], CoolingRequired
            )
        else:                                                                  # invalid rejection selection
            raise ValueError("rejection_type must be 'drycooler' or 'coolingtower'.")  # explicit error


        m_sfw = CoolingRequired / (cp_water * p["delta_T_water"])              # economizer-handled facility water mass flow [kg/s]
        Power_Pump_WE = Pump_Power(m_sfw, p["Pump_Pressure_WE"], p["Pump_e_WE"], 1000.0)  # WE pump power [kW]

        Chiller_heat_removed = CoolingRequired - WE_heat_removed              # remaining cooling duty for chiller [kW]

        m_sw = Chiller_heat_removed / (cp_water * p["delta_T_water"])          # chilled water mass flow [kg/s]
        Power_Pump_CW = Pump_Power(m_sw, p["Pump_Pressure_CW"], p["Pump_e_CW"], 1000.0)  # chilled water pump power [kW]

        if Chiller_heat_removed > 0:                                           # only compute chiller power when needed
            if rejection_type == "coolingtower":                               # tower-rejected chiller COP model
                COP_chiller = COP_gp.predict(                                  # GP COP: input is (condenser entering temp proxy, load)
                    np.array([Twb_oa + p["AT_CT"], p["Chiller_load"]]).reshape(1, 2)
                )[0] * (1.0 + p["pcop"])
            else:                                                              # drycooler case: use air-cooled COP surrogate
                COP_chiller = COP_air_gp.predict(                              # GP COP: input is (dry-bulb proxy, load)
                    np.array([p["T_oa"], p["Chiller_load"]]).reshape(1, 2)
                )[0] * (1.0 + p["pcop"])
            COP_chiller = max(float(COP_chiller), 0.1)                         # clip to avoid non-physical COP due to extrapolation
            Power_Chiller = Chiller_heat_removed / COP_chiller                 # chiller electrical power [kW]
        else:                                                                  # if economizer fully covers the load
            Power_Chiller = 0.0                                                # no chiller power

        Hrej = CoolingRequired + Power_Chiller

        Power_reject_pump = 0.0
        Power_reject_fan  = 0.0
        Water_reject_kgps = 0.0

        if rejection_type == "coolingtower":
            # All heat was rejected by the condenser water loop
            m_CT = Hrej / (cp_water * max(p["delta_T_CT"], 1e-9))
            Power_reject_pump = Pump_Power(m_CT, p["Pump_Pressure_CT"], p["Pump_e_CT"], 1000.0)
            
            print(Hrej)
            _WUE_CT, m_CT_air, _mratio, Water_evap, Water_windage, Water_DF = Cooling_Tower(
                p["T_oa"], p["RH_oa"], p["P_oa"], p["AT_CT"], Power_IT, Hrej,
                p["delta_T_CT"], p["Windage_p_CT"], p["CC_CT"], p["LGRatio_CT"]
            )

            Power_reject_fan = Fan_Power(m_CT_air, rho_oa, p["Fan_Pressure_CT"], p["Fan_e_CT"])
            Water_reject_kgps = Water_evap + Water_windage + Water_DF

        else:
            _WUE_DC, m_DC_air, m_DC_water, Water_evap, Water_drift, Water_blowdown, _Tair = Dry_Cooler(
                p["T_oa"], p["RH_oa"], p["P_oa"], p["AT_DC"], Power_IT, Hrej,
                p["delta_T_DC_water"], epsilon=p["epsilon_DC"],
                adiabatic=bool(p["adiabatic_DC"]), eta_ad=p["eta_ad_DC"],
                drift_p=p["drift_p_DC"], CC=p["CC_DC"]
            )
            # All heat was rejected by the condenser water loop
            Power_reject_pump = Pump_Power(m_DC_water, p["Pump_Pressure_DC"], p["Pump_e_DC"], 1000.0)
            Power_reject_fan  = Fan_Power(m_DC_air, rho_oa, p["Fan_Pressure_DC"], p["Fan_e_DC"])
            Water_reject_kgps = Water_evap + Water_drift + Water_blowdown

        Power_comp = np.array([
            Power_IT,
            UPS_loss,
            PD_loss,
            Light_heat,
            Power_Pump_IT,
            Power_Fan_room,
            Power_Pump_WHR,
            Power_Pump_WE,
            Power_Chiller,
            Power_Pump_CW,
            Power_reject_pump,
            Power_reject_fan,
            extra_power
        ])

        PUE_case = np.sum(Power_comp) / Power_IT
        WUE_case = Water_reject_kgps * 3600.0 / Power_IT

        results[name] = (PUE_case, WUE_case)

    PUE, WUE = results["base"]
    PUE_whr, WUE_whr = results["whr"]
    PUE_whr_hp, WUE_whr_hp = results["whr_hp"]
    return PUE, WUE, PUE_whr, WUE_whr, PUE_whr_hp, WUE_whr_hp, Q_direct_recovered, Q_hp_in, Q_hp_delivered, P_hp

def PUE_WUE_DTC_DryCooler_Watereconomizer(w):
    # Case (1): direct-to-chip cooling + dry cooler + water economizer.
    # Use w as dict (recommended) or list following param_order in the core function.
    return _PUE_WUE_liquid_watereconomizer_core(w, rejection_type="drycooler")  # call shared core with dry cooler selection


def PUE_WUE_DTC_CoolingTower_Watereconomizer(w):
    # Case (2): direct-to-chip cooling + cooling tower + water economizer.
    # Use w as dict (recommended) or list following param_order in the core function.
    return _PUE_WUE_liquid_watereconomizer_core(w, rejection_type="coolingtower")  # call shared core with tower selection


def PUE_WUE_Immersion_DryCooler_Watereconomizer(w):
    # Case (3): immersion cooling + dry cooler + water economizer.
    # NOTE: for immersion you typically set f_liquid = 1.0 and provide cp_it, rho_it for dielectric fluid if desired.
    return _PUE_WUE_liquid_watereconomizer_core(w, rejection_type="drycooler")  # call shared core with dry cooler selection


def PUE_WUE_Immersion_CoolingTower_Watereconomizer(w):
    # Case (4): immersion cooling + cooling tower + water economizer.
    # NOTE: for immersion you typically set f_liquid = 1.0 and provide cp_it, rho_it for dielectric fluid if desired.
    return _PUE_WUE_liquid_watereconomizer_core(w, rejection_type="coolingtower")  # call shared core with tower selection

