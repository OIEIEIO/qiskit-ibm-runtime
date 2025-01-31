# This code is part of Qiskit.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Resilience options."""

from typing import Sequence, Literal, get_args
from dataclasses import dataclass

from .utils import _flexible
from ..utils.deprecation import issue_deprecation_msg

ResilienceSupportedOptions = Literal[
    "noise_amplifier",
    "noise_factors",
    "extrapolator",
]
NoiseAmplifierType = Literal[
    "TwoQubitAmplifier",
    "GlobalFoldingAmplifier",
    "LocalFoldingAmplifier",
    "CxAmplifier",
]
ExtrapolatorType = Literal[
    "LinearExtrapolator",
    "QuadraticExtrapolator",
    "CubicExtrapolator",
    "QuarticExtrapolator",
]


@_flexible
@dataclass
class ResilienceOptions:
    """Resilience options.

    Args:
        noise_factors: An list of real valued noise factors that determine by what amount the
            circuits' noise is amplified.
            Only applicable for ``resilience_level=2``.
            Default: (1, 3, 5).

        noise_amplifier (DEPRECATED): A noise amplification strategy. One of ``"TwoQubitAmplifier"``,
            ``"GlobalFoldingAmplifier"``, ``"LocalFoldingAmplifier"``, ``"CxAmplifier"``.
            Only applicable for ``resilience_level=2``.
            Default: "TwoQubitAmplifier".

        extrapolator: An extrapolation strategy. One of ``"LinearExtrapolator"``,
            ``"QuadraticExtrapolator"``, ``"CubicExtrapolator"``, ``"QuarticExtrapolator"``.
            Note that ``"CubicExtrapolator"`` and ``"QuarticExtrapolator"`` require more
            noise factors than the default.
            Only applicable for ``resilience_level=2``.
            Default: "LinearExtrapolator".
    """

    noise_amplifier: NoiseAmplifierType = None
    noise_factors: Sequence[float] = (1, 3, 5)
    extrapolator: ExtrapolatorType = "LinearExtrapolator"

    @staticmethod
    def validate_resilience_options(resilience_options: dict) -> None:
        """Validate that resilience options are legal.
        Raises:
            ValueError: if any resilience option is not supported
            ValueError: if noise_amplifier is not in NoiseAmplifierType.
            ValueError: if extrapolator is not in ExtrapolatorType.
            ValueError: if extrapolator == "QuarticExtrapolator" and number of noise_factors < 5.
            ValueError: if extrapolator == "CubicExtrapolator" and number of noise_factors < 4.
        """
        if resilience_options.get("noise_amplifier", None) is not None:
            issue_deprecation_msg(
                msg="The 'noise_amplifier' resilience option is deprecated",
                version="0.12.0",
                period="1 month",
                remedy="After the deprecation period, only local folding amplification "
                "will be supported. "
                "Refer to https://github.com/qiskit-community/prototype-zne "
                "for global folding amplification in ZNE.",
            )

        for opt in resilience_options:
            if not opt in get_args(ResilienceSupportedOptions):
                raise ValueError(f"Unsupported value '{opt}' for resilience.")
        noise_amplifier = resilience_options.get("noise_amplifier") or "TwoQubitAmplifier"
        if not noise_amplifier in get_args(NoiseAmplifierType):
            raise ValueError(
                f"Unsupported value {noise_amplifier} for noise_amplifier. "
                f"Supported values are {get_args(NoiseAmplifierType)}"
            )
        extrapolator = resilience_options.get("extrapolator")
        if not extrapolator in get_args(ExtrapolatorType):
            raise ValueError(
                f"Unsupported value {extrapolator} for extrapolator. "
                f"Supported values are {get_args(ExtrapolatorType)}"
            )
        if (
            extrapolator == "QuarticExtrapolator"
            and len(resilience_options.get("noise_factors")) < 5
        ):
            raise ValueError("QuarticExtrapolator requires at least 5 noise_factors.")
        if extrapolator == "CubicExtrapolator" and len(resilience_options.get("noise_factors")) < 4:
            raise ValueError("CubicExtrapolator requires at least 4 noise_factors.")
