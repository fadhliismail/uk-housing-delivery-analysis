import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="UK Housing Delivery", layout="wide")

PROCESSED = Path("data/processed")
HDC_CODE  = "E07000011"
HDC_NAME  = "Huntingdonshire"

C_HDC    = "#e6550d"
C_ENG    = "#4393c3"
C_TARGET = "#d73027"
C_GREY   = "#bdbdbd"
C_SOC    = "#2166ac"
C_AFF    = "#f4a582"
C_SHO    = "#92c5de"

TENURE_LABELS = {
    "social_rent":      "Social rent",
    "affordable_rent":  "Affordable rent",
    "shared_ownership": "Shared ownership",
}
TENURE_COLOURS = {"Social rent": C_SOC, "Affordable rent": C_AFF, "Shared ownership": C_SHO}
TENURE_ORDER   = ["Social rent", "Affordable rent", "Shared ownership"]


@st.cache_data
def load_data():
    england    = pd.read_csv(PROCESSED / "completions_england.csv")
    net_la     = pd.read_csv(PROCESSED / "net_additions_la.csv")
    net_reg    = pd.read_csv(PROCESSED / "net_additions_regional.csv")
    affordable = pd.read_csv(PROCESSED / "affordable_completions_la.csv")
    starts_la  = pd.read_csv(PROCESSED / "starts_completions_la.csv")
    return england, net_la, net_reg, affordable, starts_la


england, net_la, net_reg, affordable, starts_la = load_data()

EOE_CODES = (
    affordable[
        (affordable["region_name"] == "East of England") &
        (affordable["ons_code"].str.startswith("E07", na=False))
    ]["ons_code"].unique()
)

with st.sidebar:
    st.markdown("### UK Housing Delivery")
    st.markdown(
        "Analysis of housing delivery across England, with a focus on "
        "Huntingdonshire District Council and the East of England."
    )
    st.markdown(
        "**Source:** MHCLG Live Tables on housing supply  \n"
        "**Coverage:** 2024-25 (provisional)"
    )
    st.markdown("---")
    st.markdown(
        "[GitHub](https://github.com/fadhliismail/uk-housing-delivery-analysis)"
    )

st.title("UK Housing Delivery")
st.caption(
    "Net additions, affordable housing, and the development pipeline across England. "
    "Data: MHCLG Live Tables, to 2024-25 (provisional)."
)

tab_nat, tab_hdc, tab_cmp, tab_aff = st.tabs([
    "National picture",
    "Huntingdonshire",
    "Compare local authorities",
    "Affordable housing",
])


# ── Tab 1: National picture ───────────────────────────────────────────────────

with tab_nat:
    net_eng = net_la[net_la["ons_code"] == "E92000001"].sort_values("year")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=net_eng["year"], y=net_eng["net_additions"],
        name="Net additions", mode="lines+markers",
        line=dict(color=C_ENG, width=2), marker=dict(size=4),
    ))
    fig.add_hline(
        y=300_000, line_dash="dash", line_color=C_TARGET,
        annotation_text="300,000 target",
        annotation_position="top right",
    )
    fig.update_layout(
        title="England net additional dwellings, 2001-02 to 2024-25",
        xaxis_title="Year", yaxis_title="Net additions",
        height=380, hovermode="x unified",
        margin=dict(t=50, b=80), xaxis_tickangle=-45,
    )
    st.plotly_chart(fig, use_container_width=True)

    comp_cols = [
        "Private Enterprise Completions",
        "Housing Association Completions",
        "Local Authority Completions",
    ]
    comp_long = (
        england[["year"] + comp_cols]
        .melt(id_vars="year", value_vars=comp_cols,
              var_name="sector", value_name="completions")
    )
    comp_long["sector"] = comp_long["sector"].str.replace(" Completions", "", regex=False)

    fig2 = px.area(
        comp_long, x="year", y="completions", color="sector",
        title="England housing completions by sector, 1946–2025",
        labels={"completions": "Completions", "year": "Year", "sector": "Sector"},
        color_discrete_map={
            "Private Enterprise": C_ENG,
            "Housing Association": "#fdae61",
            "Local Authority":    "#2ca02c",
        },
    )
    fig2.update_layout(
        height=380, hovermode="x unified",
        margin=dict(t=50, b=40),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        "England has not reached the 300,000 net additions target in any year since it was set. "
        "The 2024-25 provisional figure of 208,600 is 30% below. "
        "The long-run completions chart shows the structural root of the shortage: local authority "
        "housebuilding collapsed after the Housing Act 1980 and was never replaced at scale. "
        "Private completions have been the dominant and cyclical component since the mid-1980s, "
        "falling with each recession and rising with credit conditions."
    )


# ── Tab 2: Huntingdonshire ────────────────────────────────────────────────────

with tab_hdc:
    hdc_net = net_la[net_la["ons_code"] == HDC_CODE].set_index("year")["net_additions"]
    years_sorted = sorted(hdc_net.index)
    latest_yr = years_sorted[-1]
    prev_yr   = years_sorted[-2]

    latest_net = int(hdc_net[latest_yr])
    delta_net  = latest_net - int(hdc_net[prev_yr])

    hdc_aff_tot = (
        affordable[
            (affordable["ons_code"] == HDC_CODE) &
            (affordable["tenure"] == "total_affordable")
        ].set_index("year")["completions"]
    )
    latest_aff = int(hdc_aff_tot[latest_yr])
    delta_aff  = latest_aff - int(hdc_aff_tot[prev_yr])

    aff_rate   = round(latest_aff / latest_net * 100, 1)
    prev_rate  = round(int(hdc_aff_tot[prev_yr]) / int(hdc_net[prev_yr]) * 100, 1)
    delta_rate = round(aff_rate - prev_rate, 1)

    la_latest = (
        net_la[
            (net_la["year"] == latest_yr) &
            (net_la["ons_code"].str.startswith("E07", na=False))
        ]
        .dropna(subset=["net_additions"])
        .sort_values("net_additions", ascending=False)
        .reset_index(drop=True)
    )
    hdc_rank    = int(la_latest[la_latest["ons_code"] == HDC_CODE].index[0]) + 1
    n_districts = len(la_latest)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Net additions (2024-25)",  f"{latest_net:,}",   delta=f"{delta_net:+,}")
    c2.metric("Affordable completions",   f"{latest_aff:,}",   delta=f"{delta_aff:+,}")
    c3.metric("Affordable rate",          f"{aff_rate}%",      delta=f"{delta_rate:+.1f}pp")
    c4.metric("Shire district rank",      f"{hdc_rank} / {n_districts}",
              help="Ranked by 2024-25 net additions among shire districts. 1 = highest.")

    st.markdown("---")

    eoe_med = (
        net_la[net_la["ons_code"].isin(EOE_CODES)]
        .groupby("year")["net_additions"]
        .median()
        .reset_index()
        .rename(columns={"net_additions": "value"})
    )
    hdc_trend = net_la[net_la["ons_code"] == HDC_CODE][["year", "net_additions"]]

    lhn_years  = sorted(hdc_trend["year"].unique())
    lhn_values = [874 if y <= "2023-24" else 1213 for y in lhn_years]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hdc_trend["year"], y=hdc_trend["net_additions"],
        name=HDC_NAME, mode="lines+markers",
        line=dict(color=C_HDC, width=3), marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=eoe_med["year"], y=eoe_med["value"],
        name="East of England shire median", mode="lines",
        line=dict(color=C_GREY, width=1.5, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=lhn_years, y=lhn_values,
        name="Local Housing Need (MHCLG Standard Method)",
        mode="lines",
        line=dict(color=C_TARGET, width=1.5, dash="dash", shape="hv"),
        hovertemplate="LHN target: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        title="Huntingdonshire net additions vs Local Housing Need and East of England shire median",
        xaxis_title="Year", yaxis_title="Net additions",
        height=420, hovermode="x unified",
        margin=dict(t=50, b=80), xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Local Housing Need: 874 homes/year (MHCLG Standard Method, pre-December 2024 NPPF), "
        "rising to 1,213 from 2024-25 following the revised Standard Method introduced in the "
        "December 2024 NPPF."
    )

    col_l, col_r = st.columns(2)

    with col_l:
        hdc_sc = starts_la[starts_la["ons_code"] == HDC_CODE].sort_values("year").tail(15)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hdc_sc["year"], y=hdc_sc["all_completions"],
            name="Completions", marker_color=C_ENG,
        ))
        fig.add_trace(go.Scatter(
            x=hdc_sc["year"], y=hdc_sc["all_starts"],
            name="Starts", mode="lines+markers",
            line=dict(color="#fdae61", width=2), marker=dict(size=5),
        ))
        fig.update_layout(
            title="Huntingdonshire: starts vs completions",
            xaxis_title="Year", yaxis_title="Homes",
            height=380, hovermode="x unified",
            margin=dict(t=50, b=80), xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        hdc_aff_det = affordable[
            (affordable["ons_code"] == HDC_CODE) &
            (affordable["tenure"] != "total_affordable") &
            (affordable["year"] >= "2015-16")
        ].copy()
        hdc_aff_det["tenure_label"] = hdc_aff_det["tenure"].map(TENURE_LABELS)

        fig = px.bar(
            hdc_aff_det.sort_values("year"),
            x="year", y="completions", color="tenure_label",
            title="Huntingdonshire: affordable completions by tenure",
            labels={"completions": "Completions", "year": "Year", "tenure_label": "Tenure"},
            color_discrete_map=TENURE_COLOURS,
            category_orders={"tenure_label": TENURE_ORDER},
        )
        fig.update_layout(
            height=380, hovermode="x unified",
            margin=dict(t=50, b=80), xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)


# ── Tab 3: Compare local authorities ─────────────────────────────────────────

with tab_cmp:
    st.markdown("Compare Huntingdonshire against any shire district in England.")

    shire_la = net_la[net_la["ons_code"].str.startswith("E07", na=False)].copy()
    la_names_df = (
        shire_la[["ons_code", "authority_name"]]
        .drop_duplicates()
        .sort_values("authority_name")
    )
    name_to_code = dict(zip(la_names_df["authority_name"], la_names_df["ons_code"]))

    all_years = sorted(shire_la["year"].unique(), reverse=True)
    selected_year = st.selectbox("Year", options=all_years, index=0)

    la_yr = (
        shire_la[shire_la["year"] == selected_year]
        .dropna(subset=["net_additions"])
        .copy()
    )
    la_yr["highlight"] = la_yr["ons_code"].apply(
        lambda x: HDC_NAME if x == HDC_CODE else "Other"
    )
    hdc_val = la_yr[la_yr["ons_code"] == HDC_CODE]["net_additions"].values

    fig = px.histogram(
        la_yr, x="net_additions",
        color="highlight",
        color_discrete_map={HDC_NAME: C_HDC, "Other": "#74c476"},
        nbins=40,
        title=f"Shire district net additions distribution, {selected_year}",
        labels={"net_additions": "Net additions", "highlight": ""},
    )
    if len(hdc_val):
        fig.add_vline(
            x=float(hdc_val[0]), line_dash="dash", line_color=C_HDC,
            annotation_text=f"{HDC_NAME}: {int(hdc_val[0]):,}",
            annotation_position="top right",
        )
    fig.update_layout(height=360, margin=dict(t=50, b=40))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Compare net additions trend")

    other_names = [n for n in la_names_df["authority_name"] if n != HDC_NAME]
    selected_names = st.multiselect(
        "Select up to 3 shire districts to compare",
        options=other_names,
        default=["South Cambridgeshire", "East Cambridgeshire", "Fenland"],
        max_selections=3,
    )

    compare_codes = [name_to_code[n] for n in selected_names if n in name_to_code]
    all_codes = [HDC_CODE] + compare_codes
    code_to_name = {HDC_CODE: HDC_NAME}
    code_to_name.update({name_to_code[n]: n for n in selected_names if n in name_to_code})

    compare_df = shire_la[shire_la["ons_code"].isin(all_codes)].copy()
    compare_df["name"] = compare_df["ons_code"].map(code_to_name)

    palette = ["#4393c3", "#2ca02c", "#9467bd"]
    cmap = {HDC_NAME: C_HDC}
    for i, n in enumerate(selected_names):
        cmap[n] = palette[i % len(palette)]

    fig = px.line(
        compare_df.sort_values("year"),
        x="year", y="net_additions", color="name",
        title="Net additions trend: Huntingdonshire vs selected authorities",
        labels={"net_additions": "Net additions", "year": "Year", "name": "Authority"},
        color_discrete_map=cmap,
    )
    for trace in fig.data:
        trace.line.width = 3 if trace.name == HDC_NAME else 1.5
    fig.update_layout(
        height=420, hovermode="x unified",
        margin=dict(t=50, b=80), xaxis_tickangle=-45,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Tab 4: Affordable housing ─────────────────────────────────────────────────

with tab_aff:
    aff_eng = (
        affordable[affordable["tenure"] != "total_affordable"]
        .groupby(["year", "tenure"])["completions"]
        .sum()
        .reset_index()
    )
    aff_eng["tenure_label"] = aff_eng["tenure"].map(TENURE_LABELS)

    fig = px.area(
        aff_eng.sort_values(["year", "tenure_label"]),
        x="year", y="completions", color="tenure_label",
        category_orders={"tenure_label": TENURE_ORDER},
        title="England affordable housing completions by tenure, 1991-92 to 2024-25",
        labels={"completions": "Completions", "year": "Year", "tenure_label": "Tenure"},
        color_discrete_map=TENURE_COLOURS,
    )
    fig.update_layout(
        height=400, hovermode="x unified",
        margin=dict(t=50, b=80), xaxis_tickangle=-45,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "Social rent completions peaked in the mid-2000s and fell sharply after 2010, "
        "when the coalition government replaced capital grants for social rent with "
        "funding for affordable rent (up to 80% of market rate). The total affordable "
        "figure held up in some years, masking the tenure substitution. "
        "In high house price areas, 80% of market rent is not affordable for most "
        "households in housing need, so the tenure composition matters as much as "
        "the headline total."
    )

    st.markdown("---")

    col_l, col_r = st.columns(2)

    with col_l:
        hdc_aff2 = affordable[
            (affordable["ons_code"] == HDC_CODE) &
            (affordable["tenure"] != "total_affordable")
        ].copy()
        hdc_aff2["tenure_label"] = hdc_aff2["tenure"].map(TENURE_LABELS)

        fig = px.bar(
            hdc_aff2.sort_values("year"),
            x="year", y="completions", color="tenure_label",
            category_orders={"tenure_label": TENURE_ORDER},
            title="Huntingdonshire: affordable completions by tenure",
            labels={"completions": "Completions", "year": "Year", "tenure_label": "Tenure"},
            color_discrete_map=TENURE_COLOURS,
        )
        fig.update_layout(
            height=420, hovermode="x unified",
            margin=dict(t=50, b=80), xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        hdc_net2 = net_la[net_la["ons_code"] == HDC_CODE].set_index("year")["net_additions"]
        hdc_aff_tot2 = (
            affordable[
                (affordable["ons_code"] == HDC_CODE) &
                (affordable["tenure"] == "total_affordable")
            ].set_index("year")["completions"]
        )
        rate_df = (hdc_aff_tot2 / hdc_net2 * 100).dropna().reset_index()
        rate_df.columns = ["year", "rate"]

        fig = px.line(
            rate_df, x="year", y="rate",
            title="Huntingdonshire: affordable rate (% of net additions)",
            labels={"rate": "Affordable rate (%)", "year": "Year"},
            color_discrete_sequence=[C_HDC],
        )
        fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=4))
        fig.update_layout(
            height=420, hovermode="x unified",
            margin=dict(t=50, b=80), xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, use_container_width=True)
