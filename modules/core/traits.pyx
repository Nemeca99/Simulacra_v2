cimport numpy as np
import numpy as np
from libc.math cimport sqrt

cdef class TraitSystem:
    cdef:
        np.ndarray _trait_powers
        np.ndarray _trait_states
        dict _trait_map

    def __init__(self):
        self._trait_powers = np.zeros(0, dtype=np.float32)
        self._trait_states = np.zeros(0, dtype=np.bool_)
        self._trait_map = {}

    cpdef float calculate_power(self):
        cdef:
            float total = 0
            int i
            int n = self._trait_powers.shape[0]

        for i in range(n):
            if self._trait_states[i]:
                total += self._trait_powers[i]

        return total