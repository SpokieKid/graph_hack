import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime
from subgrounds.subgrounds import Subgrounds
from metrics import MetricsDailySnapshots
from streamlit_echarts import st_pyecharts

# Refresh every 10 seconds
REFRESH_INTERVAL_SEC = 10

sg = Subgrounds()
subgraphs = {
    "balancer-v2-polygon": sg.load_subgraph(
        "https://api.thegraph.com/subgraphs/name/dorgtech/balancer-v2-polygon"
    ),
    "uniswap-v3-polygon": sg.load_subgraph(
        "https://api.thegraph.com/subgraphs/name/steegecs/uniswap-v3-polygon"
    ),
    "quick-swap-polygon": sg.load_subgraph(
        "https://api.thegraph.com/subgraphs/name/messari/quickswap-polygon"
    ),
    "sushi-swap-polygon": sg.load_subgraph(
        "https://api.thegraph.com/subgraphs/name/messari/sushiswap-polygon"
    ),
}


def fetch_data(subgraph, amount_in_usd_gte):
    print(subgraph)
    latest_swaps = subgraph.Query.swaps(
        where=[subgraph.Swap.amountInUSD >= amount_in_usd_gte],
        orderBy=subgraph.Swap.timestamp,
        orderDirection="desc",
        first=10,
    )
    df = sg.query_df(
        [
            latest_swaps.hash,
            latest_swaps.protocol.name,
            latest_swaps.protocol.network,
            latest_swaps.timestamp,
            latest_swaps.tokenIn.symbol,
            latest_swaps.amountInUSD,
            latest_swaps.tokenOut.symbol,
            latest_swaps.amountOutUSD,
        ]
    )
    df = df.rename(columns=lambda x: x[len("swaps_") :])
    df["time"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(x).strftime("%H:%M:%S")
    )
    df["dex"] = df["protocol_name"]
    df["network"] = df["protocol_network"]

    df["amountInUSD"] = df["amountInUSD"].map("{:,.2f}".format)
    df["amountOutUSD"] = df["amountOutUSD"].map("{:,.2f}".format)
    df["swap"] = df.apply(
        lambda x: f"""\${x["amountInUSD"]} {x["tokenIn_symbol"]} 💸 \${x["amountOutUSD"]} {x["tokenOut_symbol"]}""",
        axis=1,
    )
    df["txn"] = df.apply(
        lambda x: f"""[🔗](https://polygonscan.com/tx/{x["hash"]})""",
        axis=1,
    )
    return df[["time", "dex", "network", "swap", "txn"]]


st.set_page_config(page_icon="📈")
ticker = st_autorefresh(interval=REFRESH_INTERVAL_SEC * 1000, key="ticker")
st.title("📈 PolyGraph")
st.header("Your one-stop shop to get insights into your Defi user data")

networks = st.selectbox(
    "Select networks",
    ["balancer-v2-polygon", "uniswap-v3-polygon", "sushi-swap-polygon", "quick-swap-polygon"]
)

MetricsSnapshot = MetricsDailySnapshots(subgraphs.get(networks), sg, initial_timestamp=1601322741)

with st.container():
    st_pyecharts(
        chart=MetricsSnapshot.transactions_count_chart(),
        height="450px",
        key="TransactionChart",
    )

with st.container():
    st_pyecharts(
        chart=MetricsSnapshot.active_users_chart(),
        height="450px",
        key="ActiveUsersChart",
    )

amount_in_usd_gte = st.select_slider(
    "Only display swaps with amount >=",
    value=100,
    options=[100, 1000, 10000, 100000],
    key="amount_in_usd_gte",
)

data_loading = st.text(f"[Every {REFRESH_INTERVAL_SEC} seconds] Loading data...")
df = fetch_data(subgraphs[networks], amount_in_usd_gte)
df = df.sort_values(by=["time"], ascending=False)
data_loading.text(f"[Every {REFRESH_INTERVAL_SEC} seconds] Loading data... done!")
st.markdown(df.to_markdown())

swaps = Query.swaps(
    where=[Swap.from == Variable(user_address)]
    orderBy=Swap.timestamp,
    orderDirection="desc",
    first=10
)

req_template = sg.mk_request([
  swaps.timestamp, 
  swaps.amountInUSD
])

input_address = st.text_input("Enter your address", key="input_address")
actual_req = req_template(user_address=input_address)

# def fetch_user(subgraph, user_address):
#     print(subgraph)
#     latest_swaps = subgraph.Query.swaps(
#         where=[subgraph.Swap.from == Variable('user_address')],
#         orderBy=subgraph.Swap.timestamp,
#         orderDirection="desc",
#         first=100,
#     )
    
# req_template = sg.mk_request([
#   swaps.timestamp
# ])

# user_address = st.text_input("Enter user address", key="user_address")
# actual_req = req_template(user_address)
# data = sg.execute(actual_req)
# user_data = fetech_user(subgraphs[networks], user_address)
# st.markdown(user_data.to_markdown())