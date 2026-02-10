"""
Calculator module for mutual fund investments.
Handles SIP and Lumpsum calculations with tax considerations.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, Tuple


# Tax configuration for FY 2026-27
TAX_CONFIG = {
    "EQUITY_LTCG_THRESHOLD": 125000,  # ₹1.25 lakh
    "EQUITY_LTCG_RATE": 12.5,  # 12.5% on gains above threshold
    "EQUITY_STCG_RATE": 20.0,  # 20% on all gains
    "DEBT_SLABS": [
        {"upper": 300000, "rate": 0},
        {"upper": 750000, "rate": 5},
        {"upper": 1000000, "rate": 10},
        {"upper": 1250000, "rate": 15},
        {"upper": 1500000, "rate": 20},
        {"upper": float('inf'), "rate": 30},
    ]
}


def calculate_tax_equity(gain: float, holding_period_months: int, tax_type: str = "LTCG") -> Dict:
    """
    Calculate tax on equity mutual fund gains.
    
    Args:
        gain: Capital gain amount in rupees
        holding_period_months: Number of months held
        tax_type: "LTCG" for long-term (>12 months) or "STCG" for short-term (<=12 months)
    
    Returns:
        Dictionary with tax details
    """
    if gain <= 0:
        return {
            "gain": gain,
            "tax_applicable": False,
            "tax_amount": 0,
            "gain_after_tax": gain,
            "effective_tax_rate": 0,
            "holding_period_months": holding_period_months
        }
    
    # Determine if LTCG or STCG based on holding period
    is_ltcg = holding_period_months > 12
    
    if is_ltcg:
        # LTCG: Tax only on gains exceeding ₹1.25 lakh at 12.5%
        if gain > TAX_CONFIG["EQUITY_LTCG_THRESHOLD"]:
            taxable_gain = gain - TAX_CONFIG["EQUITY_LTCG_THRESHOLD"]
            tax_amount = taxable_gain * (TAX_CONFIG["EQUITY_LTCG_RATE"] / 100)
            tax_applicable = True
        else:
            tax_amount = 0
            tax_applicable = False
    else:
        # STCG: 20% tax on all gains
        tax_amount = gain * (TAX_CONFIG["EQUITY_STCG_RATE"] / 100)
        tax_applicable = True
    
    gain_after_tax = gain - tax_amount
    effective_rate = (tax_amount / gain * 100) if gain > 0 else 0
    
    return {
        "gain": round(gain, 2),
        "tax_applicable": tax_applicable,
        "tax_type": "LTCG" if is_ltcg else "STCG",
        "tax_amount": round(tax_amount, 2),
        "gain_after_tax": round(gain_after_tax, 2),
        "effective_tax_rate": round(effective_rate, 2),
        "holding_period_months": holding_period_months,
        "tax_rate_applied": TAX_CONFIG["EQUITY_LTCG_RATE"] if is_ltcg else TAX_CONFIG["EQUITY_STCG_RATE"]
    }


def calculate_tax_debt(gain: float, investor_slab: str = "30%") -> Dict:
    """
    Calculate tax on debt mutual fund gains (taxed as per income slab).
    
    Args:
        gain: Capital gain amount in rupees
        investor_slab: Investor's tax slab ("0%", "5%", "10%", "15%", "20%", "30%")
    
    Returns:
        Dictionary with tax details
    """
    slab_rates = {
        "0%": 0,
        "5%": 5,
        "10%": 10,
        "15%": 15,
        "20%": 20,
        "30%": 30
    }
    
    if gain <= 0 or investor_slab not in slab_rates:
        return {
            "gain": gain,
            "tax_applicable": True if gain > 0 else False,
            "tax_amount": 0,
            "gain_after_tax": gain,
            "effective_tax_rate": 0,
            "tax_slab": investor_slab
        }
    
    tax_rate = slab_rates[investor_slab]
    tax_amount = gain * (tax_rate / 100)
    gain_after_tax = gain - tax_amount
    
    return {
        "gain": round(gain, 2),
        "tax_applicable": True,
        "tax_amount": round(tax_amount, 2),
        "gain_after_tax": round(gain_after_tax, 2),
        "effective_tax_rate": round(tax_rate, 2),
        "tax_slab": investor_slab,
        "tax_rate_applied": tax_rate
    }



def calculate_sip(
    monthly_investment: float,
    annual_return_rate: float,
    years: int,
    start_date: datetime = None,
    fund_type: str = "equity",
    investor_tax_slab: str = "30%",
    calculate_tax: bool = True
) -> Dict:
    """
    Calculate maturity amount for SIP (Systematic Investment Plan) investment.
    
    Args:
        monthly_investment: Monthly investment amount in rupees
        annual_return_rate: Expected annual return rate (in percentage)
        years: Investment period in years
        start_date: Investment start date
        fund_type: "equity" or "debt"
        investor_tax_slab: Tax slab for debt funds ("0%", "5%", "10%", "15%", "20%", "30%")
        calculate_tax: Whether to calculate and apply taxes
    
    Returns:
        Dictionary with calculation details including tax impact
    """
    if monthly_investment <= 0 or annual_return_rate < 0 or years <= 0:
        return {"error": "Invalid input values"}
    
    # Convert annual return to monthly rate
    monthly_rate = annual_return_rate / 12 / 100
    
    # Number of months
    months = years * 12
    
    # SIP Formula: FV = P * [((1 + r)^n - 1) / r] * (1 + r)
    # Where P = monthly payment, r = monthly return rate, n = number of months
    
    if monthly_rate == 0:
        # If no return, it's simple multiplication
        maturity_amount = monthly_investment * months
    else:
        maturity_amount = monthly_investment * (
            (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        )
    
    # Total investment
    total_invested = monthly_investment * months
    
    # Gain
    gain = maturity_amount - total_invested
    
    # Gain percentage
    gain_percentage = (gain / total_invested * 100) if total_invested > 0 else 0
    
    result = {
        "maturity_amount": round(maturity_amount, 2),
        "total_invested": round(total_invested, 2),
        "gain": round(gain, 2),
        "gain_percentage": round(gain_percentage, 2),
        "monthly_investment": monthly_investment,
        "annual_return": annual_return_rate,
        "years": years,
        "months": months,
        "fund_type": fund_type,
        "calculate_tax": calculate_tax
    }
    
    # Apply taxes if requested
    if calculate_tax:
        holding_period_months = months
        
        if fund_type.lower() == "equity":
            tax_info = calculate_tax_equity(gain, holding_period_months)
            result["tax_info"] = tax_info
            result["maturity_after_tax"] = round(total_invested + tax_info["gain_after_tax"], 2)
        else:  # debt
            tax_info = calculate_tax_debt(gain, investor_tax_slab)
            result["tax_info"] = tax_info
            result["maturity_after_tax"] = round(total_invested + tax_info["gain_after_tax"], 2)
            result["investor_tax_slab"] = investor_tax_slab
    
    return result


def calculate_lumpsum(
    principal: float,
    annual_return_rate: float,
    years: int,
    start_date: datetime = None,
    fund_type: str = "equity",
    investor_tax_slab: str = "30%",
    calculate_tax: bool = True
) -> Dict:
    """
    Calculate maturity amount for Lumpsum investment.
    
    Args:
        principal: Lumpsum investment amount in rupees
        annual_return_rate: Expected annual return rate (in percentage)
        years: Investment period in years
        start_date: Investment start date
        fund_type: "equity" or "debt"
        investor_tax_slab: Tax slab for debt funds ("0%", "5%", "10%", "15%", "20%", "30%")
        calculate_tax: Whether to calculate and apply taxes
    
    Returns:
        Dictionary with calculation details including tax impact
    """
    if principal <= 0 or annual_return_rate < 0 or years <= 0:
        return {"error": "Invalid input values"}
    
    # Future Value = P * (1 + r)^n
    # Where P = principal, r = annual return rate, n = years
    
    annual_rate = annual_return_rate / 100
    maturity_amount = principal * ((1 + annual_rate) ** years)
    
    # Gain
    gain = maturity_amount - principal
    
    # Gain percentage
    gain_percentage = (gain / principal * 100) if principal > 0 else 0
    
    result = {
        "maturity_amount": round(maturity_amount, 2),
        "principal": round(principal, 2),
        "gain": round(gain, 2),
        "gain_percentage": round(gain_percentage, 2),
        "annual_return": annual_return_rate,
        "years": years,
        "fund_type": fund_type,
        "calculate_tax": calculate_tax
    }
    
    # Apply taxes if requested
    if calculate_tax:
        holding_period_months = years * 12
        
        if fund_type.lower() == "equity":
            tax_info = calculate_tax_equity(gain, holding_period_months)
            result["tax_info"] = tax_info
            result["maturity_after_tax"] = round(principal + tax_info["gain_after_tax"], 2)
        else:  # debt
            tax_info = calculate_tax_debt(gain, investor_tax_slab)
            result["tax_info"] = tax_info
            result["maturity_after_tax"] = round(principal + tax_info["gain_after_tax"], 2)
            result["investor_tax_slab"] = investor_tax_slab
    
    return result


def compare_investments(
    monthly_sip: float,
    lumpsum: float,
    annual_return_rate: float,
    years: int,
    fund_type: str = "equity",
    investor_tax_slab: str = "30%",
    calculate_tax: bool = True
) -> Dict:
    """
    Compare SIP and Lumpsum investment strategies.
    
    Args:
        monthly_sip: Monthly SIP amount
        lumpsum: Lumpsum investment amount
        annual_return_rate: Expected annual return rate
        years: Investment period
        fund_type: "equity" or "debt"
        investor_tax_slab: Tax slab for debt funds
        calculate_tax: Whether to calculate taxes
    
    Returns:
        Comparison dictionary
    """
    sip_result = calculate_sip(monthly_sip, annual_return_rate, years, 
                               fund_type=fund_type, 
                               investor_tax_slab=investor_tax_slab,
                               calculate_tax=calculate_tax)
    lumpsum_result = calculate_lumpsum(lumpsum, annual_return_rate, years, 
                                       fund_type=fund_type, 
                                       investor_tax_slab=investor_tax_slab,
                                       calculate_tax=calculate_tax)
    
    if "error" in sip_result or "error" in lumpsum_result:
        return {"error": "Invalid input values"}
    
    total_sip_invested = monthly_sip * years * 12
    
    # Comparison with tax consideration
    if calculate_tax:
        sip_maturity = sip_result.get("maturity_after_tax", sip_result["maturity_amount"])
        lumpsum_maturity = lumpsum_result.get("maturity_after_tax", lumpsum_result["maturity_amount"])
    else:
        sip_maturity = sip_result["maturity_amount"]
        lumpsum_maturity = lumpsum_result["maturity_amount"]
    
    return {
        "sip": sip_result,
        "lumpsum": lumpsum_result,
        "difference": round(sip_maturity - lumpsum_maturity, 2),
        "better_option": "SIP" if sip_maturity > lumpsum_maturity else "Lumpsum",
        "total_sip_invested": round(total_sip_invested, 2)
    }


def calculate_required_return(
    principal: float,
    target_amount: float,
    years: int
) -> Dict:
    """
    Calculate required annual return rate to achieve target amount.
    
    Args:
        principal: Initial investment
        target_amount: Target maturity amount
        years: Investment period
    
    Returns:
        Required return rate and details
    """
    if principal <= 0 or target_amount <= principal or years <= 0:
        return {"error": "Invalid input values"}
    
    # Using formula: r = (FV/PV)^(1/n) - 1
    required_rate = ((target_amount / principal) ** (1 / years) - 1) * 100
    
    return {
        "required_return_percentage": round(required_rate, 2),
        "principal": principal,
        "target_amount": target_amount,
        "years": years
    }


def calculate_sip_with_hold_period(
    monthly_investment: float,
    investment_years: int,
    hold_years: int,
    annual_return_rate: float,
    fund_type: str = "equity",
    investor_tax_slab: str = "30%",
    calculate_tax: bool = True
) -> Dict:
    """
    Calculate SIP with a holding period (no new investments during hold period).
    
    Args:
        monthly_investment: Monthly investment amount in rupees
        investment_years: Years during which active investments are made
        hold_years: Years to hold the investment without adding new amounts
        annual_return_rate: Expected annual return rate (in percentage)
        fund_type: "equity" or "debt"
        investor_tax_slab: Tax slab for debt funds
        calculate_tax: Whether to calculate and apply taxes
    
    Returns:
        Dictionary with detailed breakdown
    """
    if monthly_investment <= 0 or investment_years <= 0 or hold_years < 0 or annual_return_rate < 0:
        return {"error": "Invalid input values"}
    
    # Phase 1: Investment Period - Calculate maturity
    monthly_rate = annual_return_rate / 12 / 100
    investment_months = investment_years * 12
    
    if monthly_rate == 0:
        maturity_after_investment = monthly_investment * investment_months
    else:
        maturity_after_investment = monthly_investment * (
            (((1 + monthly_rate) ** investment_months - 1) / monthly_rate) * (1 + monthly_rate)
        )
    
    total_invested = monthly_investment * investment_months
    gain_during_investment = maturity_after_investment - total_invested
    
    # Phase 2: Hold Period - Compound growth on maturity amount
    annual_rate = annual_return_rate / 100
    final_maturity = maturity_after_investment * ((1 + annual_rate) ** hold_years)
    
    # Total gains
    total_gain = final_maturity - total_invested
    total_gain_percentage = (total_gain / total_invested * 100) if total_invested > 0 else 0
    
    # Year-wise breakdown
    year_wise_data = []
    
    # During investment phase
    for year in range(1, investment_years + 1):
        months = year * 12
        if monthly_rate == 0:
            amount = monthly_investment * months
        else:
            amount = monthly_investment * (
                (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
            )
        invested = monthly_investment * months
        gain = amount - invested
        
        year_wise_data.append({
            "year": year,
            "phase": "Investment",
            "invested": round(invested, 2),
            "amount": round(amount, 2),
            "gain": round(gain, 2)
        })
    
    # During hold phase
    for hold_year in range(1, hold_years + 1):
        amount = maturity_after_investment * ((1 + annual_rate) ** hold_year)
        gain = amount - total_invested
        
        year_wise_data.append({
            "year": investment_years + hold_year,
            "phase": "Hold",
            "invested": round(total_invested, 2),
            "amount": round(amount, 2),
            "gain": round(gain, 2)
        })
    
    result = {
        "type": "SIP",
        "monthly_investment": monthly_investment,
        "investment_years": investment_years,
        "hold_years": hold_years,
        "annual_return": annual_return_rate,
        "total_invested": round(total_invested, 2),
        "maturity_after_investment": round(maturity_after_investment, 2),
        "gain_during_investment": round(gain_during_investment, 2),
        "final_maturity": round(final_maturity, 2),
        "total_gain": round(total_gain, 2),
        "total_gain_percentage": round(total_gain_percentage, 2),
        "year_wise_data": year_wise_data,
        "fund_type": fund_type,
        "calculate_tax": calculate_tax
    }
    
    # Apply taxes if requested
    if calculate_tax:
        # Total holding period = investment years + hold years
        holding_period_months = (investment_years + hold_years) * 12
        
        if fund_type.lower() == "equity":
            tax_info = calculate_tax_equity(total_gain, holding_period_months)
            result["tax_info"] = tax_info
            result["final_maturity_after_tax"] = round(total_invested + tax_info["gain_after_tax"], 2)
        else:  # debt
            tax_info = calculate_tax_debt(total_gain, investor_tax_slab)
            result["tax_info"] = tax_info
            result["final_maturity_after_tax"] = round(total_invested + tax_info["gain_after_tax"], 2)
            result["investor_tax_slab"] = investor_tax_slab
    
    return result


def calculate_lumpsum_with_hold_period(
    principal: float,
    investment_years: int,
    hold_years: int,
    annual_return_rate: float,
    fund_type: str = "equity",
    investor_tax_slab: str = "30%",
    calculate_tax: bool = True
) -> Dict:
    """
    Calculate Lumpsum with a holding period.
    
    Args:
        principal: Lumpsum investment amount in rupees
        investment_years: Years for investment (no additional investments)
        hold_years: Years to hold without any changes
        annual_return_rate: Expected annual return rate (in percentage)
        fund_type: "equity" or "debt"
        investor_tax_slab: Tax slab for debt funds
        calculate_tax: Whether to calculate and apply taxes
    
    Returns:
        Dictionary with detailed breakdown
    """
    if principal <= 0 or investment_years <= 0 or hold_years < 0 or annual_return_rate < 0:
        return {"error": "Invalid input values"}
    
    annual_rate = annual_return_rate / 100
    
    # Phase 1: Investment Period (Lumpsum grows for investment_years)
    maturity_after_investment = principal * ((1 + annual_rate) ** investment_years)
    gain_during_investment = maturity_after_investment - principal
    
    # Phase 2: Hold Period (Further growth)
    final_maturity = maturity_after_investment * ((1 + annual_rate) ** hold_years)
    
    # Total gains
    total_gain = final_maturity - principal
    total_gain_percentage = (total_gain / principal * 100) if principal > 0 else 0
    
    # Year-wise breakdown
    year_wise_data = []
    
    # During investment phase
    for year in range(1, investment_years + 1):
        amount = principal * ((1 + annual_rate) ** year)
        gain = amount - principal
        
        year_wise_data.append({
            "year": year,
            "phase": "Investment",
            "invested": round(principal, 2),
            "amount": round(amount, 2),
            "gain": round(gain, 2)
        })
    
    # During hold phase
    for hold_year in range(1, hold_years + 1):
        amount = maturity_after_investment * ((1 + annual_rate) ** hold_year)
        gain = amount - principal
        
        year_wise_data.append({
            "year": investment_years + hold_year,
            "phase": "Hold",
            "invested": round(principal, 2),
            "amount": round(amount, 2),
            "gain": round(gain, 2)
        })
    
    result = {
        "type": "Lumpsum",
        "principal": principal,
        "investment_years": investment_years,
        "hold_years": hold_years,
        "annual_return": annual_return_rate,
        "total_invested": round(principal, 2),
        "maturity_after_investment": round(maturity_after_investment, 2),
        "gain_during_investment": round(gain_during_investment, 2),
        "final_maturity": round(final_maturity, 2),
        "total_gain": round(total_gain, 2),
        "total_gain_percentage": round(total_gain_percentage, 2),
        "year_wise_data": year_wise_data,
        "fund_type": fund_type,
        "calculate_tax": calculate_tax
    }
    
    # Apply taxes if requested
    if calculate_tax:
        # Total holding period = investment years + hold years
        holding_period_months = (investment_years + hold_years) * 12
        
        if fund_type.lower() == "equity":
            tax_info = calculate_tax_equity(total_gain, holding_period_months)
            result["tax_info"] = tax_info
            result["final_maturity_after_tax"] = round(principal + tax_info["gain_after_tax"], 2)
        else:  # debt
            tax_info = calculate_tax_debt(total_gain, investor_tax_slab)
            result["tax_info"] = tax_info
            result["final_maturity_after_tax"] = round(principal + tax_info["gain_after_tax"], 2)
            result["investor_tax_slab"] = investor_tax_slab
    
    return result
