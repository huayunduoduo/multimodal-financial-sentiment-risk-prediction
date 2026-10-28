import akshare as ak
# 获取股票日线行情数据
stock_data = ak.stock_zh_a_daily(symbol="sz000001", start_date="2025-04-01", end_date="2025-05-01")
print(stock_data)