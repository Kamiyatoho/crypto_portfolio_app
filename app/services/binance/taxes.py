from datetime import datetime

# French crypto tax calculator module
# PFU (Prélèvement Forfaitaire Unique) = 12.8% income tax + 17.2% social contributions = 30% flat rate

INCOME_TAX_RATE = 0.128
SOCIAL_CONTRIBUTIONS_RATE = 0.172
PFU_RATE = INCOME_TAX_RATE + SOCIAL_CONTRIBUTIONS_RATE


def calculate_net_gain(realized_gains: float, realized_losses: float) -> float:
    """
    Compute the net gain for a given period by offsetting losses against gains.

    :param realized_gains: Total realized profits (positive floats)
    :param realized_losses: Total realized losses (positive floats)
    :return: Net gain floored at zero (losses beyond gains do not give negative tax base)
    """
    net = realized_gains - realized_losses
    return max(net, 0.0)


def calculate_tax(net_gain: float) -> float:
    """
    Calculate the flat PFU tax on a net gain.

    :param net_gain: Net gain as computed by calculate_net_gain
    :return: Tax amount owed under PFU rules
    """
    if net_gain <= 0:
        return 0.0
    return net_gain * PFU_RATE


def calculate_yearly_tax(realized_gains: float, realized_losses: float, year: int = None) -> float:
    """
    Convenience function to compute net gain and PFU tax for a given year.

    :param realized_gains: Total realized profits for the year
    :param realized_losses: Total realized losses for the year
    :param year: (Optional) Year for reporting; not used in computation but for clarity
    :return: Tax amount owed
    """
    net = calculate_net_gain(realized_gains, realized_losses)
    tax = calculate_tax(net)
    return tax


# Example usage:
# gains_2024 = 10000.0
# losses_2024 = 2000.0
# tax_due = calculate_yearly_tax(gains_2024, losses_2024)
# print(f"Tax due for 2024: {tax_due:.2f} EUR")