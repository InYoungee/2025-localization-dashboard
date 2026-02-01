import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("data/localization_portfolio_clean_data.csv")

# Data type cleanup
df['Total WC'] = (df['Total WC'].astype(str).str.replace(',', '', regex=False)
                  .str.replace('-', '', regex=False).str.strip())
df['Total WC'] = pd.to_numeric(df['Total WC'], errors='coerce')

df['Due Date'] = pd.to_datetime(
    df['Due Date'].astype(str) +'/2025',
    format='%m/%d/%Y',
    errors='coerce'
)
df['Date Rcvd'] = pd.to_datetime(
    df['Date Rcvd'].astype(str) +'/2025',
    format='%m/%d/%Y',
    errors='coerce'
)

project_types = ["All"] + sorted(
    df["Request Type"].dropna().unique().tolist())

# --- overall stats  ---
total_wc = df["Total WC"].sum()
total_projects = len(df)
games_covered = df["Game"].nunique()

st.set_page_config(layout="wide")

with st.sidebar:
    st.header("	📊 :red[OVERVIEW]")
    st.markdown("---")
    
    st.subheader("Total Word Count")
    st.metric(label="Total WC", value=f"{total_wc:,}", label_visibility="collapsed")
    st.markdown("---")

    st.subheader("Total Projects")
    selected_type = st.selectbox(
        "Select project type",
        project_types,
        index=0
    )

    # --- Filter logic ---
    if selected_type == "All":
        filtered_df = df
    else:
        filtered_df = df[df["Request Type"] == selected_type]

    total_projects_filtered = len(filtered_df)

    st.metric(label="", value=f"{total_projects_filtered:,}")
    st.markdown("---")

    st.subheader("Games Covered")
    st.metric(label="Games", value=f"{games_covered}", label_visibility="collapsed")

# --- Footer ---
    st.divider()
    st.caption(" Inyoung Kim · 2025 | Built with Python & Streamlit")
    st.caption("[GitHub](https://github.com/InYoungee) | [LinkedIn](https://www.linkedin.com/in/inyoungee/)")


# --- Main page ---
#st.title("2025 Localization Project Dashboard")
# --- Main page ---
st.markdown("""
    <div style="
        background-color: #1a3a5c;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    ">
        <h1 style="color: white; margin: 0;">2025 Localization Project Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

st.write("Hover over charts for detailed insights per game.")


# --- Total WC: Month & Quarter ---
monthly_wc = (
    df
    .groupby(df["Date Rcvd"].dt.to_period("M"))["Total WC"]
    .sum()
    .reset_index()
)
monthly_wc["Date"] = monthly_wc["Date Rcvd"].dt.to_timestamp()

quarterly_wc = (
    df
    .groupby(df["Date Rcvd"].dt.to_period("Q"))["Total WC"]
    .sum()
    .reset_index()
)
quarterly_wc["Quarter Start"] = quarterly_wc["Date Rcvd"].dt.to_timestamp()

QUARTER_WIDTH_MS = 80 * 24 * 60 * 60 * 1000


fig_total_wc = go.Figure()

# Quarterly bars spanning full quarter
fig_total_wc.add_trace(
    go.Bar(
        x=quarterly_wc["Quarter Start"],
        y=quarterly_wc["Total WC"],
        name="Quarterly Total WC",
        width=QUARTER_WIDTH_MS,
        marker_color="rgba(100, 149, 237, 0.35)",
        offset=0
    )
)

# Monthly line
fig_total_wc.add_trace(
    go.Scatter(
        x=monthly_wc["Date"],
        y=monthly_wc["Total WC"],
        mode="lines+markers",
        name="Monthly Total WC",
        line=dict(color="rgb(220, 20, 60)", width=3)
    )
)

fig_total_wc.update_layout(
    title="Total Word Count (2025)",
    #xaxis_title="Time",
    yaxis_title="Total Word Count",
    barmode="overlay",
    #legend_title="Aggregation Level",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1

    )
)

st.plotly_chart(fig_total_wc, use_container_width=True)
st.markdown('---')

# --- Monthly WC by game ---
monthly_game_wc = (
    df
    .assign(Month=df["Date Rcvd"].dt.to_period("M").dt.to_timestamp())
    .groupby(["Month", "Game"], as_index=False)["Total WC"]
    .sum()
)

monthly_game_wc["Month"] = monthly_game_wc["Month"].dt.strftime("%b")

heatmap_df = monthly_game_wc.pivot(
    index="Game",
    columns="Month",
    values="Total WC"
)

fig, ax = plt.subplots(figsize=(8, 4), dpi=100)

sns.heatmap(
    heatmap_df,
    cmap="Blues",
    linewidths=0.5,
    ax=ax,
    annot_kws={"size": 3}
)
ax.collections[0].colorbar.ax.tick_params(labelsize=6)

ax.set_title("Monthly Word Count by Game", y=1.05, size=8)
ax.set_xlabel("")
ax.set_ylabel("")
ax.tick_params(axis="x", rotation=45, labelsize=6)
ax.tick_params(axis="y", labelsize=6)

plt.tight_layout()

st.pyplot(fig)
st.markdown('---')

# --- LQA + Translation ---
col1, col2 = st.columns(2)
with col1:
    project_type = (pd.crosstab(df["Game"], df["Request Type"])[["Trans", "LQA"]].reset_index())

    type_frame = project_type.melt(
        id_vars="Game",
        value_vars=["Trans", "LQA"],
        var_name="Request Type",
        value_name="Project Count"
    )

    summary = (
        type_frame
        .pivot(index="Game", columns="Request Type", values="Project Count")
        .fillna(0)
    )
    summary["LQA_pct"] = summary["LQA"] / (summary["Trans"] + summary["LQA"]) * 100
    summary["Total"] = summary["Trans"] + summary["LQA"]
    summary = summary.sort_values("Total", ascending=False).reset_index()

    fig_type = go.Figure()

    # Translation bar
    fig_type.add_trace(go.Bar(
        x=summary["Game"],
        y=summary["Trans"],
        name="Translation",
        marker_color="steelblue"
    ))

    # LQA bar
    fig_type.add_trace(go.Bar(
        x=summary["Game"],
        y=summary["LQA"],
        name="LQA",
        marker_color="coral"
    ))

    # LQA percentage text
    fig_type.add_trace(go.Scatter(
        x=summary["Game"],
        y=summary["Total"],
        text=summary["LQA_pct"].map(lambda x: f"{x:.0f}%"),
        mode="text",
        textposition="top center",
        textfont=dict(size=12, color="black"),
        showlegend=False
    ))

    fig_type.update_layout(
        barmode="stack",
        title="Number of Translation and LQA Projects by Game",
        xaxis_title="Game",
        yaxis_title="Number of Projects",
        legend_title="Type",
        bargap=0.2,
        height=600
    )

    st.plotly_chart(fig_type, use_container_width=True)

# --- WC by game ---
with col2:
    wc_by_game = (df.groupby("Game", as_index=False)["Total WC"].sum().sort_values("Total WC", ascending=False))
    fig = px.bar(
        wc_by_game,
        x="Game",
        y="Total WC",
        color="Total WC",
        color_continuous_scale="Blues",
        title="Total Word Count by Game (2025)",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Game",
        yaxis_title="Total Word Count",
        template="plotly_white",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown('---')

# --- Avg WC by game ---
wc_by_game_bubble = (df.groupby("Game")["Total WC"].sum()              )

trans_project = (df[df["Request Type"] == "Trans"].groupby("Game").size().rename("Trans_Project"))
game_metrics = trans_project.to_frame().join(wc_by_game_bubble)
game_metrics["Avg_WC_per_Project"] = game_metrics["Total WC"] / game_metrics["Trans_Project"]


game_options = ["All"] + game_metrics.reset_index()["Game"].tolist()

selected_games = st.multiselect(
    "Select Games",
    options=game_options,
    default=["All"]
)

if "All" in selected_games:
    filtered_metrics = game_metrics
else:
    filtered_metrics = game_metrics[game_metrics.index.isin(selected_games)]


scatter = px.scatter(filtered_metrics.reset_index(),
                    x="Trans_Project",
                    y="Total WC",
                    size="Avg_WC_per_Project",
                    color="Game",
                    hover_name="Game",
                    size_max=60,
                    labels={
                        "Trans_Project": "Number of Trans Projects",
                        "Total WC": "Total Word Count",
                        "Avg_WC_per_Project": "Avg WC per Project"
                    },
                    title="Average Word Count per Trans Project by Game"
                    )
scatter.update_traces(hovertemplate="<b>%{hovertext}</b><br>" +
    "Trans Projects: %{x}<br>" +
    "Total WC: %{y:,}<br>" +
    "Avg WC / Project: %{marker.size:,.0f}<extra></extra>")
scatter.update_layout(height=600)

st.plotly_chart(scatter, use_container_width=True)
st.markdown('---')


# --- WC distribution by team ---
col1, col2 = st.columns(2)

# --- In-house Avg WC ---
with col1:
    inhouse_trans = df[(df["Request Type"] == "Trans") & (df["Assignee"].str.startswith("Trans_", na=False))]
    monthly_inhouse_wc = (
        inhouse_trans
        .groupby(inhouse_trans["Date Rcvd"].dt.to_period("M"))["Total WC"]
        .sum()
        .reset_index()
    )
    monthly_inhouse_wc["Month"] = monthly_inhouse_wc["Date Rcvd"].dt.to_timestamp()

    num_translators = (inhouse_trans["Assignee"].nunique())

    monthly_inhouse_wc["Avg WC per Translator"] = (monthly_inhouse_wc["Total WC"] / num_translators)

    total_2025_wc = inhouse_trans["Total WC"].sum()

    avg_yearly_wc_per_translator = total_2025_wc / num_translators

    fig = go.Figure()

    # Monthly average WC (left y-axis)
    fig.add_trace(
        go.Scatter(
            x=monthly_inhouse_wc["Month"],
            y=monthly_inhouse_wc["Avg WC per Translator"],
            mode="lines+markers",
            name="Monthly Avg WC per Translator",
            line=dict(color="#1f77b4"),
            yaxis="y1"
        )
    )

    # Yearly average WC (right y-axis)
    fig.add_trace(
        go.Scatter(
            x=monthly_inhouse_wc["Month"],
            y=[avg_yearly_wc_per_translator] * len(monthly_inhouse_wc),
            mode="lines",
            name="Yearly Avg WC per Translator",
            line=dict(dash="dash", color="#ff7f0e"),
            yaxis="y2"
        )
    )

    fig.update_layout(
        title="Monthly vs Yearly Avg Trans WC per In-house Translator",
        xaxis=dict(title="Month"),

        yaxis=dict(
            title="Monthly Avg WC per Translator",
            tickformat=",",
            titlefont=dict(color="#1f77b4")
        ),

        yaxis2=dict(
            title="Yearly Avg WC per Translator",
            overlaying="y",
            side="right",
            tickformat=",",
            showgrid=False,
            titlefont=dict(color="#ff7f0e")
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Workload Distribution ---
with col2:
    view = st.toggle("Show by In-House / Vendor", value=False)

    if not view:
        # In-house linguist distribution (by project count)
        trans_linguists = df[df["Request Type"] == "Trans"]["Assignee"].value_counts()
        fig_pie = px.pie(
            labels=trans_linguists.index,
            values=trans_linguists.values,
            names=trans_linguists.index,
            title="In-House Linguist Distribution (by Project Count)",
            hole=0.4
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")

    else:
        # In-house team vs vendor distribution (by word count)
        total_wc = df["Total WC"].sum()
        vendor_wc = (
            df.groupby("Assignee")["Total WC"].sum()
            .loc[["Vendor_M", "Vendor_E"]]
            .sum()
        )
        wc_distribut = pd.DataFrame({
            "Work Type": ["Outsourced", "In-House"],
            "Total WC": [vendor_wc, total_wc - vendor_wc]
        })
        fig_pie = px.pie(
            wc_distribut,
            names="Work Type",
            values="Total WC",
            title="In-House vs Vendor Distribution (by Word Count)",
            hole=0.4
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")

    st.plotly_chart(fig_pie, use_container_width=True)

