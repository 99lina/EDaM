import pandas as pd
import altair as alt


from .helpers import build_vega_altair_format_expr, build_vega_altair_format_expr_datetime


def render_vlines(filtered_data: pd.DataFrame, all_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(
        filtered_data
    ).mark_rule(
        strokeWidth=2
    ).encode(
        x=alt.X(
            'x:Q',
            axis=alt.Axis(
                orient='top',
                values=filtered_data.x.to_list(),
                labelExpr=build_vega_altair_format_expr(filtered_data),
                title=None,
                ticks=False,
                domain=True,
                labelAngle=270,
                labelOverlap=False, 
            ),
            scale=alt.Scale(zero=False)
        ),
        color=alt.Color(
            'label:N',
            legend=None
        ).scale(
            domain=all_data["label"].to_list() # also works with just the series, but type checker complains because a pd.series is not a Sequence
        )
    ).properties(height=50)


def render_hist(filtered_data: pd.DataFrame,  all_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(filtered_data).mark_bar(opacity=0.75, color="#C1E3DD").encode(
        x=alt.X('x_start:Q', title="Value distribution", scale=alt.Scale(zero=False)),
        x2=alt.X2('x_end:Q'),
        y=alt.Y('height:Q', title='Count'),
        y2=alt.datum(0)
    )


def render_range(filtered_data: pd.DataFrame, all_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(
        filtered_data
    ).mark_rule(
        strokeWidth=6,
        strokeCap="butt",
    ).encode(
        x=alt.X(
            'x_adj:Q',
            axis=alt.Axis(
                values=[all_data["center"].iloc[0]],
                grid=True,
                labels=False,
                domain=False,
                title=None
            ),
            scale=alt.Scale(zero=False)
        ),
        x2='center:Q',
        y=alt.Y(
            'label:N',
            axis=alt.Axis(
                grid=True,
                labelFlush=False,
                title=None,
                domain=True
            )
        ),
        color=alt.Color(
            'label:N',
            legend=None
        ).scale(
            domain=all_data["label"].to_list()  # also works with just the series, but type checker complains because a pd.series is not a Sequence
        ),
        tooltip=["label", "deviation"],
        strokeDash=alt.condition(
            alt.datum.is_left, 
            alt.value([2, 2]), 
            alt.value([0])
        )
    )

def render_categorical_distribution(filtered_data: pd.DataFrame, all_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(filtered_data).mark_bar(
        opacity=0.75,
        color="#C1E3DD"
    ).encode(
        x=alt.X(
            'value:N',
            title="Value distribution",
            sort='-y',
            axis=alt.Axis(labelAngle=-90)
        ),
        y=alt.Y(
            'height:Q',
            title='Count',
            scale=alt.Scale(zero=True)
        ),
        tooltip=[
            alt.Tooltip('value:N', title='Value'),
            alt.Tooltip('height:Q', title='Count')
        ]
    )

def render_date_vlines(filtered_data: pd.DataFrame, all_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(
        filtered_data
    ).mark_rule(
        strokeWidth=2
    ).encode(
        x=alt.X(
            'x:T',
            axis=alt.Axis(
                orient='top',
                values=filtered_data.x.to_list(),
                labelExpr=build_vega_altair_format_expr_datetime(filtered_data),
                title=None,
                ticks=False,
                domain=True,
                labelAngle=270,
                labelOverlap=False,
            ),
            scale=alt.Scale(zero=False)
        ),
        color=alt.Color(
            'label:N',
            legend=None
        ).scale(
            domain=all_data["label"].to_list()
        )
    ).properties(height=50)


def render_date_hist(filtered_data: pd.DataFrame, all_data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(
        filtered_data
    ).mark_bar(
        opacity=0.75,
        color="#C1E3DD"
    ).encode(
        x=alt.X(
            'x_start:T',
            title="Value distribution",
            scale=alt.Scale(zero=False)
        ),
        x2=alt.X2('x_end:T'),
        y=alt.Y('height:Q', title='Count'),
        y2=alt.datum(0)
    )