import * as Plot from "@observablehq/plot"
import * as d3 from 'd3';

// Function to create an array of Date objects for every hour of a selected date
function createDateArray(selectedDate) {
  var dateArray = [];

  // Set the selected date to the beginning of the day
  selectedDate.setHours(0, 0, 0, 0);

  // Loop through each hour of the day and create Date objects
  for (var i = 0; i < 24; i++) {
    var hourDate = new Date(selectedDate);
    hourDate.setHours(i);
    dateArray.push({datetime: hourDate, common_name: undefined, scientific_name: undefined, count: undefined});
  }

  return dateArray;
}

export function plotBars(detectionsData){
  return Plot.plot({
    marginLeft: 120,
    width: 800,
    grid: true,
    x: {
      label: "Anzahl Gesamt",
      labelAnchor: "center",
      labelArrow: null,
    },
    y: {
      label: null
    },
    marks: [
      Plot.ruleX([0]),
      Plot.barX(detectionsData, Plot.groupY({x: "sum"}, {x: "count", y: "common_name", sort: {y: "x", reverse: true}}))
    ]
  })
}

export function plotCells(detectionsData){
  if (!detectionsData.length > 0){
    return
  }
  const selectedDate = new Date(detectionsData[0].datetime); // Replace '2024-04-07' with your selected date
  const arraydate = createDateArray(selectedDate)
  return Plot.plot({
    padding: 0,
    marginLeft: 120,
    width: 800,
    grid: true,
    x: {
      tickFormat: d3.timeFormat("%H"),
      interval: d3.utcHour,
      ticks: d3.timeHour,
      domain: arraydate.map(x => x.datetime),
      label: "Uhrzeit",
      labelArrow: null,
    },
    y: {label: null},
    // y: {label: null, tickFormat: null, tickSize: null, axis: "right"},  // Hide Species Labels
    color: {type: "linear", scheme: "YlGn", zero: true, legend: false},
    marks: [
      Plot.cell(detectionsData, {x: "datetime", y: "common_name", fill: "count", inset: 0.5, sort: {y: "-fill"}}),
      Plot.text(detectionsData, {x: "datetime", y: "common_name", text: "count", fill: d => d.count > 20 ? "white" : "black", title: "title"})
    ]
  })
}

export function plotSpectrogram(spectrogramData) {
  return Plot.plot({
    grid: true,
    color: {scheme: "inferno"},
    y: {axis: null},
    x: {axis: null},
    marks: [
      Plot.raster(spectrogramData, {x: "x", y: "y", fill: "fill", interpolate: Plot.interpolateNearest})
    ]
  })
}
