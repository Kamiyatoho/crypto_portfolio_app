from flask import Blueprint, render_template, request, jsonify
from app.services.binance_service import BinanceService

# Define the Blueprint for dashboard routes
bp = Blueprint('dashboard', __name__)

# Initialize the BinanceService once for the blueprint
binance_service = BinanceService()

@bp.route('/')
def dashboard():
    """
    Render the main dashboard page with portfolio overview.
    """
    # Fetch current portfolio data
    portfolio = binance_service.get_portfolio_data()
    # Render the template with portfolio context
    return render_template('dashboard.html', portfolio=portfolio)

@bp.route('/sync', methods=['POST'])
def sync_data():
    """
    Trigger an incremental sync with Binance and return status.
    """
    try:
        binance_service.sync()
        return jsonify({'status': 'success', 'message': 'Sync completed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/portfolio', methods=['GET'])
def api_portfolio():
    """
    Provide portfolio data as JSON for frontend consumption.
    """
    try:
        portfolio = binance_service.get_portfolio_data()
        return jsonify(portfolio)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/performance', methods=['GET'])
def api_performance():
    """
    Return performance metrics (returns, drawdowns) as JSON.
    """
    try:
        perf = binance_service.get_performance_metrics()
        return jsonify(perf)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/taxes', methods=['GET'])
def api_taxes():
    """
    Return tax calculation results for the given year.
    Query param: year (int)
    """
    year = request.args.get('year', type=int)
    try:
        tax_info = binance_service.calculate_taxes(year)
        return jsonify(tax_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
