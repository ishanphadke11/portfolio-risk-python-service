from flask import Blueprint, request, jsonify
from app.services.stock_data import fetch_stock_prices, InvalidTickerError, NoDataError
from app.services.factor_data import load_factor_data, FactorDataError
from app.services.portfolio import calculate_portfolio_returns, allign_data
from app.services.regression import run_factor_regression, format_regression_results, RegressionError

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/api/analysis/factor-regression", methods=["POST"])
def factor_regression():
    # Run fama french 5 factor regression on portfolio

    data = request.get_json()

    # validate request
    if not data or 'holdings' not in data:
        return jsonify({"error": "Missing holdings", "code": "BAD_REQUEST"}), 400

    holdings = data['holdings']
    start_date = data.get('startDate')
    end_date = data.get('endDate')

    if not holdings:
        return jsonify({"error": "Holdings list is empty", "code": "BAD_REQUEST"}), 400

    if not start_date or not end_date:
        return jsonify({"error": "Missing startDate or endDate", "code": "BAD_REQUEST"}), 400

    tickers = [h['ticker'] for h in holdings]

    try:
        # milestone 2: fetch data
        prices = fetch_stock_prices(tickers, start_date, end_date)
        factor_data = load_factor_data(start_date, end_date)

        # milestone 3: portfolio returns
        portfolio_returns = calculate_portfolio_returns(holdings, prices)
        aligned = allign_data(portfolio_returns, factor_data)

        # milestone 4: regression
        results = run_factor_regression(aligned)
        formatted = format_regression_results(results)

        return jsonify(formatted), 200

    except InvalidTickerError as e:
        return jsonify({"error": str(e), "code": "INVALID_TICKER"}), 404

    except NoDataError as e:
        return jsonify({"error": str(e), "code": "NO_DATA"}), 404

    except FactorDataError as e:
        return jsonify({"error": str(e), "code": "FACTOR_DATA_ERROR"}), 404

    except RegressionError as e:
        return jsonify({"error": str(e), "code": "REGRESSION_ERROR"}), 400

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}", "code": "INTERNAL_ERROR"}), 500
