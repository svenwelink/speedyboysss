import functionsForDashboard
import plotly_express as px
import pandas as pd
import streamlit as st
import math
import plotly.graph_objects as go

views = ["Totaal gelopen afstand",
         "Afstand per dag",
         "Aandeel per persoon",
         "Eddington getal"]

def getView(viewName, df):
    if viewName == "Totaal gelopen afstand":
        distanceRunProgressionView(df)
    elif viewName == "Aandeel per persoon":
        distancePerPersonView(df)
    elif viewName == "Eddington getal":
        eddingtongView(df)
    elif viewName == "Afstand per dag":
        distancePerDayView(df)

    return

def distanceRunProgressionView(df=pd.DataFrame):
    # DataFrames
    dataPerDay = functionsForDashboard.getDataDistanceOverYear(df)
    hoverData = (
        dataPerDay
        .pivot(index="Datum", columns="Type", values="Afstand")
        .reset_index()
    )

    hoverData["Verschil"] = (
        hoverData["Totale afstand"] - hoverData["Doel"]
    )

    dataPerDay = dataPerDay.merge(
        hoverData[["Datum", "Totale afstand", "Doel", "Verschil"]],
        on="Datum",
        how="left"
    )

    plotPerDay = px.line(
        dataPerDay,
        x="Datum",
        y="Afstand",
        color="Type",
        color_discrete_map={
            "Totale afstand": "#00AAFF",
            "Doel": "#FFAA00"
        },
        custom_data=["Totale afstand", "Doel", "Verschil"]
    )

    plotPerDay.update_traces(
        hovertemplate=
        "<b>%{x|%d-%m-%Y}</b><br>" +
        "Totale afstand: %{customdata[0]:.1f} km<br>" +
        "Doel: %{customdata[1]:.1f} km<br>" +
        "Verschil: %{customdata[2]:.1f} km" +
        "<extra></extra>"
    )

    # Data values 
    distanceToday = round(float(str(dataPerDay[(dataPerDay["Datum"] == min(pd.Timestamp.today().normalize(), pd.Timestamp(2026, 12, 31))) &
                       (dataPerDay["Type"] == "Totale afstand")]["Afstand"].values).strip("[]")), 1)
    distanceGoalToday = round(float(str(dataPerDay[(dataPerDay["Datum"] == min(pd.Timestamp.today().normalize(), pd.Timestamp(2026, 12, 31))) &
                       (dataPerDay["Type"] == "Doel")]["Afstand"].values).strip("[]")), 1)
    totalGoalDistance = str(dataPerDay[(dataPerDay["Datum"] == pd.Timestamp(2026, 12, 31)) &
                       (dataPerDay["Type"] == "Doel")]["Afstand"].values).strip("[].")

    # Data values zoom settings
    endDate = min(pd.Timestamp.today().normalize(), pd.Timestamp(2026, 12, 31))
    startDate = endDate - pd.DateOffset(months=1)
    yMin = math.floor(min(dataPerDay[dataPerDay["Datum"] == startDate]["Afstand"]) / 100) * 100
    yMax = math.ceil(max(distanceToday, distanceGoalToday) / 100) * 100
    
    # Text strings
    if distanceToday < distanceGoalToday:
        text = "Dat betekend dat we op dit moment: " + str(round(distanceGoalToday - distanceToday, 1)) + " kilometer achter lopen op schema om het doel van " + totalGoalDistance + " kilometer te halen."
    else: 
        text = "Dat betekend dat we op dit moment: " + str(round(distanceToday - distanceGoalToday, 1)) + " kilometer voor lopen op schema om het doel van " + totalGoalDistance + " kilometer te halen."
    
    st.text("De totaal gelopen afstand dit jaar is: " + str(distanceToday) + " kilometer. " + text) 

    # Update plot view settings
    view = st.pills("Weergave grafiek:", ["Laatste maand", "Volledige jaar"], default="Laatste maand")

    if view == "Laatste maand":
        endDate = min(pd.Timestamp.today().normalize(), pd.Timestamp(2026, 12, 31))
        startDate = endDate - pd.DateOffset(months=1)
        yMin = math.floor(min(dataPerDay[dataPerDay["Datum"] == startDate]["Afstand"]) / 100) * 100
        yMax = math.ceil(max(distanceToday, distanceGoalToday) / 100) * 100

        plotPerDay.update_xaxes(range=[startDate, endDate])
        plotPerDay.update_yaxes(range=[yMin, yMax])
    elif view == "Volledige jaar":
        endDate = min(pd.Timestamp.today().normalize(), pd.Timestamp(2026, 12, 31))
        startDate = pd.Timestamp(2026, 1, 1)
        yMin = math.floor(min(dataPerDay[dataPerDay["Datum"] == startDate]["Afstand"]) / 100) * 100
        yMax = math.ceil(max(distanceToday, distanceGoalToday) / 100) * 100

        plotPerDay.update_xaxes(range=[startDate, endDate])
        plotPerDay.update_yaxes(range=[yMin, yMax])

    plotPerDay.update_layout(dragmode="pan")

    st.plotly_chart(plotPerDay)

    return

def distancePerPersonView(df:pd.DataFrame):
    # Data
    dfGroupedMonth = functionsForDashboard.makeDataForMonthGraph(df)
    dfGroupedMonth = dfGroupedMonth[dfGroupedMonth["Distance"] > 0]
    
    # Month slycer
    avalibleMonths = [month for id, month in functionsForDashboard.monthLabels.items() if int(id) <= (len(set(dfGroupedMonth["MonthName"])))]
    selectedMonth = st.pills("Selecteer een maand", ["Alle maanden"] + avalibleMonths, default="Alle maanden")

    # Filter the data
    if selectedMonth == "Alle maanden":
        distanceString = "dit jaar is " + str(round(dfGroupedMonth["Distance"].sum(), 1))
        dfFilterd = dfGroupedMonth
    else:
        distanceString = "in " + selectedMonth + " is " + str(round(dfGroupedMonth[dfGroupedMonth["MonthName"] ==  selectedMonth]["Distance"].sum(), 1))
        dfFilterd = dfGroupedMonth[dfGroupedMonth["MonthName"] ==  selectedMonth]
    
    # Plot the data
    plot3 = px.pie(dfFilterd, 
                values = "Distance", 
                names = "Name",
                color = dfFilterd["Name"],
                color_discrete_map = functionsForDashboard.colorMap,
                labels={"Name": "Naam",
                        "Distance": "Afstand"
                        })

    # Page
    st.text("De totaal afgelegde afstand  " + distanceString + " kilometer.")
    st.plotly_chart(plot3)

    return

def eddingtongView(df:pd.DataFrame):
    # Person selector
    personSlycer = df["Name"].unique().tolist()
    personSlycer.sort()
    personSelect = st.pills("Selecteer een naam", personSlycer, default=personSlycer[0])
    
    # Data
    eddingtonData = functionsForDashboard.getEddingtonDataForPerson(df=df[df["Name"] == personSelect])
    eddingtonNumber = eddingtonData[eddingtonData["RunCount"] >= eddingtonData["EddingtonDistance"]]["EddingtonDistance"].max()

    # Graph
    fig = go.Figure(
        data=[
            go.Bar(
                x=eddingtonData["EddingtonDistance"], 
                y=eddingtonData["RunCount"],
                marker_color="#00AAFF",
                name="Aantal dagen"),

            go.Scatter(
                x=eddingtonData["EddingtonDistance"],
                y=eddingtonData["EddingtonDistance"],
                mode="lines",
                line=dict(color="#FFAA00"),
                name="Eddington lijn")
        ]
    ) 

    fig.update_layout(
        xaxis_title="Aantal kilometers",
        yaxis_title="Aantal dagen met minimaal X km"
    )

    # Page
    fig.update_layout(showlegend=False)
    st.text("Het Eddingtong getal van " + personSelect + " is " + str(eddingtonNumber) + ". Het Eddingtongetal is het hoogste getal waarvoor je minstens X dagen een afstand van minstens X kilometer hebt gelopen.")
    st.plotly_chart(fig)
    
    return

def distancePerDayView(df:pd.DataFrame):
    # Person selector
    personSlycer = df["Name"].unique().tolist()
    personSlycer.sort()
    personSelect = st.pills("Selecteer een naam", ["Alles"] + personSlycer, default="Alles")

    # Filter the data
    if personSelect == "Alles":
        dfFilterd = df
    else:
        dfFilterd = df[df["Name"] == personSelect]

    # Create figure
    dfFilterd["Total"] = dfFilterd.groupby("Date")["Distance"].transform("sum")
    fig = px.bar(
        dfFilterd,
        x="Date",
        y="Distance",
        color="Name",
        color_discrete_map=functionsForDashboard.colorMap,
        hover_data={"Total": ":.3f"},
        labels={"Date": "Datum",
                "Name": "Naam",
                "Distance": "Afstand",
                "Total": "Totale afstand"}
    )
    
    # Zoom the figure
    endDate = min(pd.Timestamp.today().normalize(), pd.Timestamp(2026, 12, 31))
    startDate = endDate - pd.DateOffset(months=2)

    fig.update_xaxes(range=[startDate, endDate])
    fig.update_layout(dragmode="pan")

    # Page
    st.plotly_chart(fig)

    return
