#Simulateurs + maths
import math
import random
#Constantes:
PVR = 0.00033
DOSE_RESPONSE = 1.019
SHEDDING = 0.6

VIRAL_GEN = 0.1738  

MOST_HAZARD_FRAC = 0.4
FILTER_EFF = 1.0

CAR_H = 3.714
CAR_W = 2.5
CAR_L = 152.437 / 9
CAR_VOL = CAR_W * CAR_H * CAR_L

HVAC_MATRICES = {
    'Conventional':[1.0, 0.92, 0.49, 0.0],
    'Proposed':[0.05, 0.92 * 0.05, 0.49 * 0.05, 0.0],
    'Hybrid':[0.125, 0.92 * 0.125, 0.49 * 0.125, 0.0]
}

class MetroSim:
    #initialise l'état du simulateur de métro et configure les variables de base comme la capacité maximale, la ventilation (ACH) et le compte des passagers 
    def __init__(self):
        self.ach = 10.0
        self.max_cap = 126 
        self.mask_compliance = 0.0
        self.mask_eff_in = 0.0  
        self.mask_eff_out = 0.0 
        self.hvac = 'Conventional'
        
        self.pax = 0
        self.infectious = 0.0  # Actively shedding virus (Source)
        self.exposed = 0.0     # Infected during ride, but NOT shedding (Incubation)
        self.susceptible = 0.0
        self.tot_pax = 0  
        
        self.vol_most_hazard = CAR_VOL * MOST_HAZARD_FRAC
        self.vol_least_hazard = CAR_VOL * (1 - MOST_HAZARD_FRAC)

    def seed_train(self, boarding, infectious_count):
        # prépare le train au départ. Il fait monter les passagers initiaux et ajoute un passager infectieux (le patient zéro) dans le compte total
        actual_on = min(boarding, self.max_cap)
        self.pax = actual_on

        self.tot_pax = actual_on
        

        self.infectious = min(infectious_count, actual_on)
        self.exposed = 0.0

        self.susceptible = max(0.0, self.pax - self.infectious)

    def stop_at_station(self, alighting, boarding):
        #gère la dynamique à chaque arrêt. Il retire les passagers qui descendent en enlevant proportionnellement des personnes saines et infectées et ajoute les nouveaux passagers qui montent à bord.
        actual_off = min(alighting, self.pax)
        
        infectious_leaving = 0.0

        exposed_leaving = 0.0

        if self.pax > 0:
            infectious_leaving = actual_off * (self.infectious / self.pax)
            exposed_leaving = actual_off * (self.exposed / self.pax)
            
        self.pax -= actual_off
        
        actual_on = min(boarding, self.max_cap - self.pax)
        
        
        self.pax += actual_on
        self.tot_pax += actual_on
        
        self.infectious = max(0.0, self.infectious - infectious_leaving)
        
        
        self.exposed = max(0.0, self.exposed - exposed_leaving)
        self.susceptible = max(0.0, self.pax - self.infectious - self.exposed)



    def run_leg(self, travel_sec):
        #calcule la distance et le temps entre deux stations, calule la concentration du virus dans l'air selon la ventilation et le type de système HVAC et évalue la dose virale absorbée par les passagers, puis applique une formule de probabilité ppur déterminer combien de nouvellles personnes ont éét exposées au virus durant le segment de transport
        if self.pax <= 0 or self.infectious <= 0 or self.susceptible <= 0: 
            return 0.0
            
        
        
        most_hazard_ratio = self.vol_most_hazard / CAR_VOL
        
        inf_most = sum(1.0 for _ in range(int(self.infectious)) if random.random() < most_hazard_ratio)
        
        
        
        
        
        inf_least = int(self.infectious) - inf_most
        
        
        rem = self.infectious - int(self.infectious)
        
        
        inf_most += (rem * most_hazard_ratio)
        inf_least += (rem * (1 - most_hazard_ratio))

        
        susc_most = self.susceptible * most_hazard_ratio
        susc_least = self.susceptible * (1 - most_hazard_ratio)

        blockage = min(0.5 * (self.pax / self.max_cap), 0.99)
        
        
        if 'Proposed' in self.hvac:
            d = HVAC_MATRICES['Proposed']

        elif 'Hybrid' in self.hvac:
            d = HVAC_MATRICES['Hybrid']

        else:
            d = HVAC_MATRICES['Conventional']

        vent_base = (self.ach / 3600.0) * (1 - blockage) * (0.25 + 0.75 * FILTER_EFF)
        dil_most = max(self.vol_most_hazard * vent_base, 1e-9)


        dil_least = max(self.vol_least_hazard * vent_base, 1e-9)

        source_rate = VIRAL_GEN * SHEDDING * (1 - self.mask_compliance * self.mask_eff_out)
        
        conc_most = (inf_least * d[0] + inf_most * d[1]) * (source_rate / dil_most)


        conc_least = (inf_least * d[2] + inf_most * d[3]) * (source_rate / dil_least)

        dose_most = conc_most * PVR * travel_sec

        dose_least = conc_least * PVR * travel_sec

        p_mask_most = 1 - math.exp(-DOSE_RESPONSE * dose_most * (1 - self.mask_eff_in))

        p_nomask_most = 1 - math.exp(-DOSE_RESPONSE * dose_most)

        new_most = susc_most * (self.mask_compliance * p_mask_most + (1 - self.mask_compliance) * p_nomask_most)
        
        p_mask_least = 1 - math.exp(-DOSE_RESPONSE * dose_least * (1 - self.mask_eff_in))
        
        
        
        
        p_nomask_least = 1 - math.exp(-DOSE_RESPONSE * dose_least)

        
        new_least = susc_least * (self.mask_compliance * p_mask_least + (1 - self.mask_compliance) * p_nomask_least)
        
        new_cases = new_most + new_least
        self.exposed += new_cases
        
        self.susceptible = max(0.0, self.susceptible - new_cases)
        
        return new_cases
