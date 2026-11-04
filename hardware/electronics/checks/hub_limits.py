#!/usr/bin/env python3
"""Initial-tolerance DC bounds, not a transient or lifetime qualification.

INA301 SBOS713A tables 6.5; TPS2663 SLVSE94G tables 6.5/6.6;
Vishay WSL doc 30100; Panasonic ERA6AEB1052V (0.1%, 25 ppm/K).
Resistor-divider TCR requirement: <=25 ppm/K per element.
"""
import json


def divider_bounds(top, bottom, threshold, temperature, leakage=150e-9):
    error = .001 + 25e-6 * abs(temperature-25) * 1.001
    low = threshold[0] * (1+top*(1-error)/(bottom*(1+error))) - leakage*top*(1+error)
    high = threshold[1] * (1+top*(1+error)/(bottom*(1-error))) + leakage*top*(1+error)
    return low, high


def limits(temperature=125, gradient_k=10, limit_ohms=10500):
    """Worst signs combined; temperatures refer to parts, not enclosure ambient.

    A 10 K terminal temperature difference is an explicit unmeasured assumption.
    The 3 uV/K thermal-EMF allowance must be checked with the Kelvin layout.
    """
    delta = abs(temperature-25)
    uv = divider_bounds(135e3,10e3,(1.176,1.224),temperature)
    ov = divider_bounds(172e3,10e3,(1.176,1.224),temperature)
    ov_recover = divider_bounds(172e3,10e3,(1.09,1.15),temperature)
    sense_error = .01 + 75e-6*delta*1.01
    limit_error = .001 + 25e-6*delta*1.001
    # A1 offset + drift + full CMRR excursion from the 12V test condition
    # + full PSRR excursion from the 5V test condition + assumed thermal EMF.
    offset = 125e-6 + .5e-6*delta + abs(ov[1]-12)*1e-5 + (5-(3.3*.98-.01-.05))*10e-6 + 3e-6*gradient_k
    gain_error = .001 + 10e-6*delta + .0001  # Includes specified nonlinearity.
    low = ((79.2e-6*limit_ohms*(1-limit_error)-.0035)/(20*(1+gain_error))-offset)/(.01*(1+sense_error))
    high = ((80.8e-6*limit_ohms*(1+limit_error)+.0035)/(20*(1-gain_error))+offset)/(.01*(1-sense_error))
    return dict(part_temperature_C=temperature, assumed_terminal_gradient_K=gradient_k,
                trip_min_A=low, trip_nominal_A=80e-6*limit_ohms/.2, trip_max_A=high,
                control_min_V=3.3*.98-.01-.05,
                control_release_max_V=2.79*1.015*1.025,
                control_assert_min_V=2.79*.985,
                uv_rising_V=uv, ov_rising_V=ov, ov_recovery_V=ov_recover,
                protected_input_max_at_21V_W=21*high,
                backup_current_min_A=5.58/1.001, backup_current_max_A=6.42/.999,
                trip_with_1mV_overdrive_A=high+.001/(.01*(1-sense_error)),
                protected_input_max_at_ov_W=ov[1]*high,
                shunt_loss_at_trip_W=high*high*.01*(1+sense_error),
                shunt_rated_W=1 if temperature <= 70 else (170-temperature)/100,
                required_external_current_margin_A=.01,
                input_max_including_10mA_bypass_W=ov[1]*(high+.01))


if __name__=='__main__':
    print(json.dumps([limits(t) for t in (25,70,125)],indent=2))
