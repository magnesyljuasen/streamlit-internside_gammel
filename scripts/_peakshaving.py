import numpy as np

def peakshaving(energy_arr, REDUCTION):
        RHO, HEAT_CAPACITY = 0.96, 4.2
        NEW_MAX_EFFECT = max(energy_arr) - REDUCTION
        
        #Finne topper
        peakshaving_arr = np.zeros(len(energy_arr))
        for i in range(0, len(energy_arr)):
            peakshaving_arr[i] = energy_arr[i]

        max_effect_arr = np.zeros(len(energy_arr))
        for i in range(0, len(energy_arr)):
            effect = energy_arr[i]
            if effect > NEW_MAX_EFFECT:
                max_effect_arr[i] = effect - NEW_MAX_EFFECT
        
        #Lade tanken før topper, og ta bort topper
        day = 12
        for i in range(0, len(energy_arr)-day):
            peakshave = max_effect_arr[i+day]
            if peakshave > 0:
                peakshaving_arr[i+day] -= peakshave
                peakshaving_arr[i] += peakshave/6
                peakshaving_arr[i+1] += peakshave/6
                peakshaving_arr[i+2] += peakshave/6
                peakshaving_arr[i+3] += peakshave/6
                peakshaving_arr[i+4] += peakshave/6
                peakshaving_arr[i+5] += peakshave/6
            
        return peakshaving_arr, max(peakshaving_arr)