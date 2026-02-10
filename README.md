# Mutual Funds Calculator

A comprehensive web application for calculating and analyzing mutual fund investments built with Python and Streamlit.

## Features

✅ **Implemented:**
- **SIP Calculator**: Calculate maturity amount for monthly systematic investments
- **Lumpsum Calculator**: Calculate returns on one-time investments
- **Comparison Tool**: Compare SIP vs Lumpsum investment strategies side-by-side
- **Growth Holding Period Calculator**: Calculate returns with active investment period + hold period for both SIP and Lumpsum
- **Interactive Visualizations**: Charts showing investment growth over time
- **Year-wise Breakdown**: Detailed tables and analysis for each year
- **Tax Analysis**: Before and after-tax calculations based on FY 2026-27 tax rules
- **Real-time Calculations**: Instant results with customizable parameters

**Tax Features (FY 2026-27):**
- **Equity Mutual Funds**:
  - LTCG (Long-term Capital Gain, >12 months): 12.5% tax on gains exceeding ₹1.25 lakh
  - STCG (Short-term Capital Gain, ≤12 months): 20% flat tax on all gains
- **Debt Mutual Funds**: Taxed as per investor's income tax slab (0%, 5%, 10%, 15%, 20%, 30%)
- **Toggle Tax Calculations**: Enable/disable tax impact analysis for each calculator
- **Tax Breakdown**: View maturity amounts before and after tax with effective tax rates

🚀 **Coming Soon:**
- Integration with AMFI mutual fund database
- Historical NAV data visualization
- Portfolio tracking and management
- Advanced analysis with different asset classes
- Risk assessment tools

## Project Structure

```
mutual-funds-calculators/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── app.py                   # Main Streamlit application
│   └── calculator.py            # Calculation functions
├── data/                        # Data files and datasets
├── tests/                       # Unit tests
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore file
└── README.md                    # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mutual-funds-calculators.git
cd mutual-funds-calculators
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

1. Activate your virtual environment:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Run the Streamlit app:
```bash
streamlit run src/app.py
```

3. Open your browser to `http://localhost:8501`

### Available Calculators

#### SIP Calculator
- Enter monthly investment amount
- Set expected annual return percentage
- Choose investment period in years
- View maturity amount, total gain, and growth charts

#### Lumpsum Calculator
- Enter one-time investment amount
- Set expected annual return percentage
- Choose investment period
- Visualize growth trajectory

#### Compare SIP vs Lumpsum
- Compare two investment strategies side-by-side
- View maturity amounts and gains
- Determine which strategy is better for your situation

#### Growth Holding Period
- Calculate both **SIP** and **Lumpsum** returns with two phases:
  - **Investment Phase**: Active investments for specified years
  - **Hold Phase**: Compound growth without new investments for specified years
- View year-wise breakdown with detailed tables
- See how much you gain during each phase
- Visualize growth trajectory across both periods

### Customization

All calculations are fully customizable:
- Investment amounts (minimum ₹500 for SIP, ₹1000 for Lumpsum)
- Expected return rates (0-30%)
- Investment periods (1-40 years)
- Start dates

## Official Data Sources

This calculator uses expected return rates. To get actual mutual fund performance data:

### AMFI (Association of Mutual Funds in India)
- **Website**: https://www.amfiindia.com/
- **Features**: NAV data, historical performance, fund comparisons
- **NAV Downloads**: Latest and historical NAV data

### NSE (National Stock Exchange)
- **Website**: https://www.nseindia.com/
- **Features**: Market data, mutual fund listings, indices
- **Mutual Funds**: Access to mutual fund market watch

### SEBI (Securities and Exchange Board of India)
- **Website**: https://www.sebi.gov.in/
- **Features**: Investor protection guidelines, regulatory information

## Formulas Used

### SIP (Systematic Investment Plan)
```
FV = P × [((1 + r)^n - 1) / r] × (1 + r)
```
Where:
- FV = Future Value (Maturity Amount)
- P = Monthly Payment/Investment
- r = Monthly Return Rate (Annual Rate / 12 / 100)
- n = Number of Months

### Lumpsum Investment
```
FV = P × (1 + r)^n
```
Where:
- FV = Future Value (Maturity Amount)
- P = Principal Amount
- r = Annual Return Rate / 100
- n = Number of Years

## Tax Rules (FY 2026-27)

### Equity Mutual Funds
**Long-Term Capital Gains (LTCG) - Holding Period > 12 months:**
```
Tax = 0 (if gain ≤ ₹1.25 lakh)
Tax = (Gain - ₹1.25 lakh) × 12.5% (if gain > ₹1.25 lakh)
```

**Short-Term Capital Gains (STCG) - Holding Period ≤ 12 months:**
```
Tax = Gain × 20%
```

### Debt Mutual Funds
Taxed as per investor's income tax slab:
- 0% slab: No tax
- 5% slab: Gain × 5%
- 10% slab: Gain × 10%
- 15% slab: Gain × 15%
- 20% slab: Gain × 20%
- 30% slab: Gain × 30%

**Note**: Tax rules as per Budget 2026. Please verify with latest tax regulations before making investment decisions.

## Requirements

- Python 3.8 or higher
- Streamlit 1.28.1+
- Pandas 2.0.3+
- NumPy 1.24.3+
- Plotly 5.17.0+ (for visualizations)

See `requirements.txt` for complete list of dependencies.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Madgula Saikrishna

## Disclaimer

⚠️ **Important**: 
- This calculator provides estimates based on expected returns
- Actual returns may vary based on market conditions and fund performance
- Past performance is not indicative of future results
- Please consult with a certified financial advisor before making investment decisions
- This tool is for educational and informational purposes only
- The developer assumes no liability for investment decisions made using this calculator
